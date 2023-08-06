This is the utility for converting github issues to `bitbucket issues export 
format`_.

Supported features:

- Exporting issues titles, descriptions and comments
- Exporting issue metadata: milestone and assignee
- Converting github labels or other issue data to bitbucket issue status, 
  priority, version, component or kind if properly configured
- Exporting issue tracker metadata: milestones are taken from github milestones, 
  components and versions are automatically generated if they were deduced from 
  issue data according to configuration
- User and milestone renaming during export

Example usage:::

    % ./gibiexport.py --user ZyX-I leycec/raiagent --output raiagent-issues.zip
    Password for ZyX-I:
    % # Now upload raiagent-issues.zip file to bitbucket

.. image:: http://i.creativecommons.org/l/by-sa/4.0/88x31.png

This work is licensed under a `Creative Commons Attribution-ShareAlike 4.0 
International License`_.

.. _bitbucket issues export format: https://confluence.atlassian.com/pages/viewpage.action?pageId=330796872
.. _Creative Commons Attribution-ShareAlike 4.0 International License: http://creativecommons.org/licenses/by-sa/4.0/
