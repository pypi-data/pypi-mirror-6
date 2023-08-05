#!/usr/bin/python

from setuptools import setup
import codecs


with codecs.open('README.rst', encoding='utf-8') as RF:
    README = RF.read()


setup(
    name='gibiexport',
    description='Tool for exporting github issues into bitbucket issues export format',
    url='https://bitbucket.org/ZyX_I/gibiexport',
    version='0.1.1',
    author='Nikolay Pavlov',
    author_email='kp-pav@yandex.ru',
    download_url='https://bitbucket.org/ZyX_I/gibiexport/get/default.tar.bz2',
    license='CC-BY-SA-4.0',
    long_description=README,
    requires=('PyGithub', 'docopt'),
    scripts=('gibiexport.py',),
)
