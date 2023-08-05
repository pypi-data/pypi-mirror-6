#!/usr/bin/env python

from distutils.core import setup

CLASSIFIERS = """
Development Status :: 5 - Production/Stable
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Testing
""".strip().splitlines()

setup(
    name             = 'robotfixml',
    version          = '1.0',
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
