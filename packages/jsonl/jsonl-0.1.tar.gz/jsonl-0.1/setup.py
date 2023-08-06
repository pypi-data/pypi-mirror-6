#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages
    
import os

from jsonl import __version__

setup(
    name = "jsonl",
    version = __version__,
    url = 'https://bitbucket.org/sys-git/jsonl',
    packages = find_packages(),
    package_dir = {'jsonl': 'jsonl'},
    include_package_data = False,
    author = "Francis Horsman",
    author_email = "francis.horsman@gmail.com",
    description = "Standard JSON implementation creating attributed objects instead of dictionaries",
    license = "GNU General Public License",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

