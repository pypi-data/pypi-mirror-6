#!/usr/bin/env python

import glob 

from setuptools import setup

import os.path, os

setup(name='hyperglyph',
    version='0.9-20140421',
    license="MIT License",
    description='hyperglyph is ducked typed ipc over http',
    author='tef',
    author_email='tef@twentygototen.org',
    packages=['hyperglyph', 'hyperglyph.resource'],
    #scripts=glob.glob('*.py'),
    test_suite = "tests",
    install_requires = [
        "werkzeug",
        "requests",
        "pytz",
        "isodate",
    ]
)

