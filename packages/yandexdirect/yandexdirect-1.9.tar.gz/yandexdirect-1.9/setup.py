#!/usr/bin/env python
# vim: set fileencoding=utf-8:

from distutils.core import setup

VERSION = "1.9"


classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: Unix',
    'Programming Language :: Python',
    'Topic :: Utilities',
    ]

longdesc = """A simple wrapper for the Yandex.Direct API

Send your feedback to <hex@umonkey.net>
"""

setup(
    author = 'Justin Forest',
    author_email = 'hex@umonkey.net',
    classifiers = classifiers,
    description = 'Yandex.Direct API',
    long_description = longdesc,
    license = 'MIT',
    name = 'yandexdirect',
    package_dir = {'': 'src'},
    packages = ['yandexdirect'],
    requires = [],
    url = 'http://code.umonkey.net/python-yandexdirect/',
    download_url = 'http://code.umonkey.net/python-yandexdirect/archive/default.zip',
    version = VERSION
)
