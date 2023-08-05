#!/usr/bin/env python

import re
from distutils.core import setup
from os.path import join, abspath, dirname

NAME = 'robotfixml'
CLASSIFIERS = """
Development Status :: 5 - Production/Stable
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Testing
""".strip().splitlines()
with open(join(dirname(abspath(__file__)), 'src', NAME+'.py')) as src:
    VERSION = re.search("\n__version__ = '(.*)'\n", src.read()).group(1)

setup(
    name             = NAME,
    version          = VERSION,
    author           = 'Robot Framework Developers',
    author_email     = 'robotframework@gmail.com',
    url              = 'http://bitbucket.org/robotframework/fixml',
    download_url     = 'https://pypi.python.org/pypi/robotfixml',
    license          = 'Apache License 2.0',
    description      = 'A tool for fixing broken Robot Framework output files',
    long_description = open('README.rst').read(),
    keywords         = 'robotframework testing testautomation atdd xml',
    platforms        = 'any',
    classifiers      = CLASSIFIERS,
    package_dir      = {'': 'src'},
    py_modules       = ['robotfixml'],
    install_requires = ['BeautifulSoup']
)
