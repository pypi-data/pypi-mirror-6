#!/usr/bin/env python
# vim: set fileencoding=utf-8:

from distutils.core import setup


classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: Unix',
    'Programming Language :: Python',
    'Topic :: Utilities',
    ]

longdesc = """A simple CLI interface to sms.ru, can be used to access almost
all API endpoints, e.g.: send messages, query balance, display limits, etc.
"""

setup(
    author = 'Justin Forest',
    author_email = 'hex@umonkey.net',
    classifiers = classifiers,
    description = 'CLI for sms.ru',
    long_description = longdesc,
    license = 'MIT',
    name = 'python-smsru',
    package_dir = {'': 'src'},
    packages = ['smsru'],
    requires = [],
    scripts = ['smsru'],
    url = 'http://code.umonkey.net/python-smsru/',
    download_url = 'http://code.umonkey.net/python-smsru/archive/default.zip',
    version = '1.0'
)
