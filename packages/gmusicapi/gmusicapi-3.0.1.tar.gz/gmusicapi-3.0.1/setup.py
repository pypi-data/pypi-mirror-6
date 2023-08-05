#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from setuptools import setup, find_packages
import sys

#Only 2.6-2.7 are supported.
if not ((2, 6, 0) <= sys.version_info[:3] <= (2, 7, 5)):
    sys.stderr.write('gmusicapi does not officially support this Python version.\n')
    #try to continue anyway

dynamic_requires = []

if sys.version_info[:2] == (2, 6):
    dynamic_requires += ['unittest2 == 0.5.1', 'simplejson == 3.0.7']


#This hack is from http://stackoverflow.com/a/7071358/1231454;
# the version is kept in a seperate file and gets parsed - this
# way, setup.py doesn't have to import the package.

VERSIONFILE = 'gmusicapi/_version.py'

version_line = open(VERSIONFILE).read()
version_re = r"^__version__ = ['\"]([^'\"]*)['\"]"
match = re.search(version_re, version_line, re.M)
if match:
    version = match.group(1)
else:
    raise RuntimeError("Could not find version in '%s'" % VERSIONFILE)

setup(
    name='gmusicapi',
    version=version,
    author='Simon Weber',
    author_email='simon@simonmweber.com',
    url='http://pypi.python.org/pypi/gmusicapi/',
    packages=find_packages(),
    scripts=[],
    license=open('LICENSE').read(),
    description='An unofficial api for Google Play Music.',
    long_description=(open('README.rst').read() + '\n\n' +
                      open('HISTORY.rst').read()),
    install_requires=[
        'validictory == 0.9.1',    # validation
        'decorator == 3.4.0',      # keep
        'mutagen == 1.22',         # MM
        'protobuf == 2.5.0',       # MM
        'requests == 2.0.1',       # keep
        'python-dateutil == 2.1',  # MM
        'proboscis==1.2.5.3',      # testing
        'oauth2client==1.2',       # MM
        'mock==1.0.1',             # testing
        'appdirs==1.2.0',          # keep
    ] + dynamic_requires,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    include_package_data=True,
    zip_safe=False,
)
