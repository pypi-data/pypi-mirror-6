#! /usr/bin/env python

import os
from setuptools import setup, find_packages
from armory import VERSION
from armory.utils import fread

PROJECT   = "armory"
AUTHOR    = "neuroticnerd"
EMAIL     = "None"
DESC      = "A library of python and django tools and scripts."
LONG_DESC = fread('README.rst')
LICENSE   = "Apache2.0"
KEYWORDS  = "tools utilities scripts windows"
URL       = "http://packages.python.org/armory"
REQUIRES  = fread('requirements.txt', True)

# https://pypi.python.org/pypi?%3Aaction=list_classifiers
TAGS      = [
                "Development Status :: 2 - Pre-Alpha",
                "Topic :: Utilities",
                "Topic :: Software Development :: Libraries :: Python Modules",
                "License :: OSI Approved :: Apache Software License",
                "Intended Audience :: Developers",
                "Programming Language :: Python :: 2.7",
            ]


setup(
    name = PROJECT,
    version = VERSION,
    author = AUTHOR,
    author_email = EMAIL,
    description = DESC,
    license = LICENSE,
    keywords = KEYWORDS,
    url = URL,
    packages = find_packages(),
    long_description = LONG_DESC,
    install_requires = REQUIRES,
    classifiers = TAGS,
)

