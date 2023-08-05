#!/usr/bin/env python
#
#  Copyright (c) 2010-2012 Corey Goldberg (corey@goldb.org)
#  License: GNU LGPLv3
#
#  This file is part of Multi-Mechanize | Performance Test Framework
#


"""
setup.py for pyak47
"""

import os

from setuptools import setup, find_packages

from pyak47 import __version__


this_dir = os.path.abspath(os.path.dirname(__file__))


NAME = 'pyak47'
VERSION = __version__
PACKAGES = find_packages(exclude=['ez_setup'])
DESCRIPTION = 'pyak47 - Performance Test Framework'
URL = 'https://github.com/kakwa/pyak47/'
LICENSE = 'GNU LGPLv3'
f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
description = f.read()
f.close()
REQUIREMENTS = filter(None, open(os.path.join(this_dir, 'requirements.txt')).read().splitlines())
AUTHOR = 'Pierre-Francois Carpentier'
AUTHOR_EMAIL = 'carpentier.pf@gmail.com'
KEYWORDS = ('performance', 'scalability', 'load', 'test', 'testing', 'benchmark')
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Testing',
    'Topic :: Software Development :: Testing :: Traffic Generation',
    'Topic :: System :: Benchmark',
]
CONSOLE_SCRIPTS = [
    'pyak47-run = pyak47.utilities.run:main',
    'pyak47-newproject = pyak47.utilities.newproject:main',
    'pyak47-gridgui = pyak47.utilities.gridgui:main',
]


params = dict(
    name=NAME,
    version=VERSION,
    packages=PACKAGES,
    install_requires = REQUIREMENTS,

    # metadata for upload to PyPI
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=description,
    keywords=KEYWORDS,
    url=URL,
    classifiers=CLASSIFIERS,
    entry_points = { 'console_scripts': CONSOLE_SCRIPTS }
)

setup(**params)
