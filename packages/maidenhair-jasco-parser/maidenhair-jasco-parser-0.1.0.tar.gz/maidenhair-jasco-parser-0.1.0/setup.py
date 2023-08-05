#!/usr/bin/env python
# coding=utf-8
"""
maidenhair-jasco-parser

(C) 2013 hashnote.net, Alisue
"""
name = 'maidenhair-jasco-parser'
version = '0.1.0'
author = 'Alisue'
author_email = 'lambdalisue@hashnote.net'

import os
from setuptools import setup, find_packages

setup(
    name=name,
    version=version,
    description = "maidenhair parser plugin for reading JASCO txt file",
    long_description=__doc__,
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
    keywords = "maidenhair, JASCO, parser",
    author = "Alisue",
    author_email = "lambdalisue@hashnote.net",
    license = 'MIT',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    exclude_package_data = {'': ['README.md']},
    zip_safe = True,
    install_requires=[
        'maidenhair',
        'numpydoc',
    ],
    entry_points={
        'maidenhair.plugins': [
            'parsers.JASCOParser = maidenhair_jasco_parser:JASCOParser',
        ],
    },
)
