'''
    MyKeys setup
    ~~~~~~~~~~~~

    Package setup script.

    :copyright: Copyright 2014 by Vlad Riscutia  
    :license: FreeBSD, see LICENSE file
'''
import sys
from setuptools import setup, find_packages

import mykeys


long_desc = '''
MyKeys is a simple library to help with roaming various OAuth keys and secrets.

OAuth key/secret pairs granted by various websites (like Twitter, GoodReads etc.)
shouldn't be checked into public repositories. Storing them in config files
or env variables is possible, but makes roaming them inconvenient.

MyKeys provides a simple interface to parse key/secret pairs from a standard
config file.

This file can be pushed to a private repository, roamed via DropBox etc. so
it can be moved across machines privately.
'''

setup(
    name = "MyKeys",
    version = mykeys.__version__,
    url = "http://github.com/vladris/mykeys",
    download_url = "http://pypi.python.org/pypi/MyKeys",
    license = "FreeBSD",
    author = "Vlad Riscutia",
    author_email = "riscutiavlad@gmail.com",
    description = "Key/secret provider",
    long_description = long_desc,
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python"
    ],
    platforms = "any",
    packages = find_packages(exclude=['test']),
    include_package_data = True,
    entry_points = {
        'console_scripts': [
            "mykeys = mykeys.cmdline:main"
        ]
    },
    install_requires = [],
    test_suite = "nose.collector"
)

