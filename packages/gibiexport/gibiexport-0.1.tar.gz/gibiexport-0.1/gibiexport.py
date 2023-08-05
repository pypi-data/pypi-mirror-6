#!/usr/bin/python
# vim:fileencoding=utf-8

'''
Utility for converting github issues to bitbucket issues export format

Usage:
    gibiexport.py [(--user USER [--password PASSWORD])] [--output FILE]
                  [(--settings-file FILE | --ignore-settings)] URL
    gibiexport.py -h | --help

Options:
    -u, --user USER           Authenicate using given USER. If it is not given, 
                              do not authenicate.
    -p, --password PASSWORD   Authenicate using given PASSWORD. If it is not 
                              given gibiexport.py will prompt it on the 
                              command-line.
    -o, --output FILE         Write result to given file. If this option is given 
                              then it will create a zip archive in the location 
                              described by FILE. If this option is not given then 
                              unzipped json will be outputted to the terminal.
    -s, --settings-file FILE  Take settings from the given FILE. Default is from 
                              $XDG_CONFIG_HOME/gibiexport/config.json (default 
                              for $XDG_CONFIG_HOME is $HOME/.config).
    -i, --ignore-settings     Ignore settings. Default settings will also be 
                              ignored.
    URL                       Github URL. Should have form [WHATEVER/]USER/REPO, 
                              e.g. https://github.com/MarcWeber/vim-addon-manager 
                              or just MarcWeber/vim-addon-manager.
    -h, --help                Show this help.

Settings:
    Settings are by default taken from $XDG_CONFIG_HOME/gibiexport/config.json. 
    It is a JSON file which should contain a dictionary with the following keys 
    (all are optional).

    user        Username used to log in to github. Note: like with --user if 
                this setting is specified, but password is not then password 
                will be asked on the command-line.
    password    Password used to log in to github.
    users       A list of 3-tuples (lists with three items). First element is 
                format suitable for str.format (e.g. "{login}"), second is regex 
                and third is replacement string in the same format.

                This setting is used to tell gibiexport about what github user 
                stand for what bitbucket user.

                First format string gets keyword arguments from 
                github.NamedUser.NamedUser instance’s raw_data and no positional 
                parameters. Hence you may use "{email}", "{login}", "{name}" and 
                many other user-related items in the format.

                Second string is a regex that will be compiled by re.compile() 
                and then matched by compiled_regex.search(). Matching is done 
                against string obtained from the first format string.

                Third format string is only used in case regex matched 
                something. It receives the same keyword arguments first format 
                string does and additionally positional arguments from capturing 
                groups defined in the second regex. The result of the formatting 
                will be used as the bitbucket user name.
    milestones
    components
    kinds
    statuses
    priorities
    versions    Just like above, but for the first string github.Issue.Issue 
                instance’s raw_data will be used and the result will be used to 
                determine component, kind, status or version of the issue 
                respectively. In addition to keyword arguments first positional 
                parameter will be a NUL-separated labels list. This parameter 
                will always start and end with a NUL. It will also be the first 
                positional parameter in the third formatting string.

                Hint: match against "{html_url}" if you want repository-specific 
                settings.

                In case nothing matched here are the defaults:
                    "milestone": milestone from github
                    "component": None
                    "kind": "bug"
                    "priority": "major"
                    "status": "open" (for open issues) or "resolved" (for closed)
                    "version": None

    default_kinds
                Like users, but using github.Repository.Repository instance’s 
                raw_data. Uses "bug" if nothing matched.

Default configuration:
'''

from __future__ import unicode_literals

import docopt
import json
import sys
import os
import re
from zipfile import ZipFile
from github import Github
from getpass import getpass
from itertools import chain
from types import StringTypes
from collections import defaultdict
from copy import deepcopy
from datetime import datetime


def format_timestamp(dt):
    if dt is None:
        return None
    if isinstance(dt, StringTypes):
        dt = datetime.strptime(dt, '%a, %d %b %Y %H:%M:%S %Z')
    return dt.isoformat()


EVENT_COMMENT_CONTENT = '{description}\n\n\u2192 <<cset {hex}>>'

def get_event_comment(event, issue, id_gen, cfg):
    if event.commit_id:
        content = (EVENT_COMMENT_CONTENT
                   .format(**cfg.get_changeset(event.commit_id)))
    else:
        content = ''

    return {
        'content': content,
        'created_on': format_timestamp(event.created_at),
        'id': id_gen.id,
        'issue': issue.number,
        'updated_on': None,
        'user': cfg.get_user(issue, event.actor),
    }


def log_field_change(comment_json, last, field, new_value):
    log_json = {
        'changed_from': last[field],
        'changed_to': new_value,
        'comment': comment_json['id'],
        'created_on': comment_json['created_on'],
        'field': field,
        'issue': comment_json['issue'],
        'user': comment_json['user'],
    }
    last[field] = log_json['changed_to']
    return log_json


class EventsMapNS:
    @staticmethod
    def _dummy(event, issue, id_gen, cfg, last):
        return [], []

    subscribed = _dummy
    mentioned = _dummy

    del _dummy

    @staticmethod
    def closed(event, issue, id_gen, cfg, last):
        comment_json = get_event_comment(event, issue, id_gen, cfg)
        log_json = log_field_change(comment_json, last, 'status', 'resolved')
        return [comment_json], [log_json]

    @staticmethod
    def reopened(event, issue, id_gen, cfg, last):
        comment_json = get_event_comment(event, issue, id_gen, cfg)
        log_json = log_field_change(comment_json, last, 'status', 'open')
        return [comment_json], [log_json]

    merged = closed

    @staticmethod
    def referenced(event, issue, id_gen, cfg, last):
        comment_json = get_event_comment(event, issue, id_gen, cfg)
        return [comment_json], []

    @staticmethod
    def assigned(event, issue, id_gen, cfg, last):
        comment_json = get_event_comment(event, issue, id_gen, cfg)
        log_json = log_field_change(comment_json, last, 'assignee',
                                    cfg.get_user(issue, event.actor))
        return [comment_json], [log_json]


def format_issue(issue, result, id_gen, cfg):
    issue_json = {
        'assignee': cfg.get_user(issue, issue.assignee),
        'component': cfg.get_component(issue),
        'content': issue.body,
        'content_updated_on': format_timestamp(issue.last_modified),
        'created_on': format_timestamp(issue.created_at),
        'id': issue.number,
        'kind': cfg.get_kind(issue),
        'milestone': cfg.get_milestone(issue),
        'priority': cfg.get_priority(issue),
        'reporter': cfg.get_user(issue, issue.user),
        'status': cfg.get_status(issue),
        'title': issue.title,
        'updated_on': format_timestamp(issue.updated_at),
        'version': cfg.get_version(issue),
        'watchers': [],  # TODO
        'voters': [],
    }
    issue_json['edited_on'] = issue_json['content_updated_on']

    jsons = defaultdict(list)
    jsons['issues'] = [issue_json]

    last = {
        'status': 'new',
        'assignee': None,
    }

    for comment in issue.get_comments():
        comment_json = {
            'content': comment.body,
            'created_on': format_timestamp(comment.created_at),
            'id': id_gen.id,
            'issue': issue.number,
            'updated_on': format_timestamp(comment.updated_at),
            'user': cfg.get_user(issue, comment.user),
        }
        jsons['comments'].append(comment_json)

    for event in issue.get_events():
        try:
            formatter = getattr(EventsMapNS, event.event)
        except AttributeError:
            sys.stderr.write('Got event with unknown type: {0}\n'
                             .format(event.event))
            continue
        ret = formatter(event, issue, id_gen, cfg, last)
        jsons['comments'].extend(ret[0])
        jsons['logs'].extend(ret[1])

    for key in ('component', 'version'):
        if issue_json[key]:
            obj = {'name': issue_json[key]}
            if obj not in result[key + 's']:
                jsons[key + 's'].append(obj)

    for key, val in jsons.items():
        result[key].extend(val)


class IdGen(object):
    def __init__(self):
        self._id = 0

    @property
    def id(self):
        self._id += 1
        return self._id


class Config(object):
    def __init__(self, g, repo, config):
        self.g = g
        self.repo = repo
        self.user_cache = {}
        self.config = deepcopy(config)
        for key in ('users', 'milestones', 'components', 'kinds', 'statuses',
                    'priorities', 'versions', 'default_kinds'):
            if key in self.config:
                self.config[key] = tuple((
                    (f1, re.compile(regex), f2)
                    for f1, regex, f2 in self.config[key]
                ))
            else:
                self.config[key] = ()

    def get_from_key(self, key, args, kwargs, default):
        for f1, reobj, f2 in self.config[key]:
            s = f1.format(*args, **kwargs)
            match = reobj.search(s)
            if not match:
                continue
            args = args + match.groups()
            return f2.format(*args, **kwargs)
        return default

    @staticmethod
    def get_labels_arg(issue):
        return '\0' + ('\0'.join((label.name for label in issue.labels))) + '\0'

    def get_milestone(self, issue):
        milestone = issue.milestone.title if issue.milestone else None
        return self.get_from_key('milestones', self.get_labels_arg(issue),
                                 issue.raw_data, milestone)

    def get_user(self, issue, user):
        if user is None:
            return None
        if isinstance(user, StringTypes):
            try:
                user = self.user_cache[user]
            except KeyError:
                user = self.g.get_user(user)
        return self.get_from_key('users', (), user.raw_data, user.login)

    def get_component(self, issue):
        return self.get_from_key('components', self.get_labels_arg(issue),
                                 issue.raw_data, None)

    def get_kind(self, issue):
        return self.get_from_key('kinds', self.get_labels_arg(issue),
                                 issue.raw_data, 'bug')

    def get_priority(self, issue):
        return self.get_from_key('priorities', self.get_labels_arg(issue),
                                 issue.raw_data, 'major')

    def get_status(self, issue):
        default = 'open' if issue.state == 'open' else 'resolved'
        return self.get_from_key('statuses', self.get_labels_arg(issue),
                                 issue.raw_data, default)

    def get_version(self, issue):
        return self.get_from_key('versions', self.get_labels_arg(issue),
                                 issue.raw_data, None)

    def get_default_kind(self):
        return self.get_from_key('default_kinds', (), self.repo.raw_data, 'bug')

    def get_changeset(self, hex):
        try:
            commit = self.repo.get_commit(hex)
        except Exception:
            # FIXME
            return {'description': '', 'hex': hex}
        return {'description': commit.commit.message, 'hex': commit.commit.sha}


def getconfig():
    args = docopt.docopt(__doc__)

    if not args['--settings-file']:
        config_dir = os.environ.get('XDG_CONFIG_HOME',
                            os.path.expanduser(os.path.join('~', '.config')))
        config_file = os.path.join(config_dir, 'gibiexport', 'config.json')
    else:
        config_file = args['--settings-file']

    if not args['--ignore-settings']:
        try:
            with open(config_file) as CF:
                config = json.load(CF)
        except IOError:
            config = DEFAULT_CONFIG
    else:
        config = {}

    if not args['--user'] and 'user' in config:
        args['--user'] = config['user']
        args['--password'] = config.get('password')

    if args['--user'] and not args['--password']:
        args['--password'] = getpass('Password for ' + args['--user'] + ': ')

    url = args['URL'].rsplit('/', 2)
    if len(url) <= 1:
        raise ValueError('Expected URL in format USER/REPO, got {0}'
                         .format(args['URL']))
    args['USER'] = url[-2]
    args['REPO'] = url[-1]
    args['URL'] = args['USER'] + '/' + args['REPO']

    return args, config


ISSUE_STATES = ('open', 'closed')

DEFAULT_CONFIG = {
    'users': [
        ['{login}', '^ZyX-I$', 'ZyX_I'],
    ],
    'kinds': [
        ['{0}', '\0(enhancement|bug)\0', '{1}'],
        ['{0}', '\0(discussion|question)\0', 'proposal'],
    ],
    'statuses': [
        ['{0}', '\0(invalid|duplicate|wontfix)\0', '{1}'],
    ],
}

__doc__ += json.dumps(DEFAULT_CONFIG, indent=4)

def main():
    args, config = getconfig()

    g = Github(args['--user'], args['--password'])
    repo = g.get_repo(args['URL'])

    idgen = IdGen()
    cfg = Config(g, repo, config)

    result = {
        'issues': [],
        'comments': [],
        'attachments': [],
        'logs': [],
        'meta': {
            'default_assignee': None,
            'default_component': None,
            'default_kind': cfg.get_default_kind(),
            'default_milestone': None,
            'default_version': None,
        },
        'components': [],
        'milestones': [{'name': milestone.title}
                       for milestone in repo.get_milestones()],
        'versions': [],
    }

    for issue in chain(*[repo.get_issues(state=state)
                         for state in ISSUE_STATES]):
        format_issue(issue, result, idgen, cfg)

    if args['--output']:
        with ZipFile(args['--output'], 'w') as archive:
            result_str = json.dumps(result, separators=(',', ':'))
            archive.writestr('db-1.0.json', result_str)
    else:
        json.dump(result, sys.stdout, indent=2, separators=(',', ': '))


if __name__ == '__main__':
    main()
