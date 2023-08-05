# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from distutils.core import setup
from thetvdb_api import (__title__, __version__, __author__)

setup(
  name = __title__,
  version = __version__,
  author = __author__,
  author_email = 'none',
  description = 'A Python API for theTVDB.',
  url = 'https://bitbucket.org/Julien-D/thetvdb_api',
  license = 'GNU General Public License v3 (GPLv3)',
  long_description = 'thetvdb_api is a very simple to use Python API for theTVDB.com.',
  packages=find_packages(),
  zip_safe=False,
  classifiers=['Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Home Automation',
    'Topic :: Multimedia',
    'Topic :: Utilities']
)