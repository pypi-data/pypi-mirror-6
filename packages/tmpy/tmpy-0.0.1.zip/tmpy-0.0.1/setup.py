#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import (absolute_import, division, print_function, unicode_literals)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = "tmpy",
    packages = ["tmpy"],
    package_dir = {"tmpy": "tmpy"},
    package_data = {
        "tmpy": [
            "misc/stopwords/*.dat",
            "misc/texts/*.xml",
            "misc/texts/*.txt",
            "misc/texts/acq/*",
            "misc/texts/crude/*",
            "misc/texts/txt/*"
            ]
        },
    license = "BSD",
    version = "0.0.1",
    description = "a text mining framework in Python",
    author = "Junwen Huang",
    author_email = "hjwdhjwd@gmail.com",
    url = "https://github.com/fyears/tmpy",
    platforms = ["all"],
    keywords = ["text mining"],
    install_requires = [
        "numpy",
        "scipy",
        "pandas",
        "nltk",
        "xmltodict"
        ],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Text Processing :: General",
        "Topic :: Text Processing :: Linguistic"
        ],
    long_description = "tmpy is text minging framework in Python, modeled after the tm R package. Yet it makes good use of the existing scipy, numpy, pandas, nltk, and xmltodict packages, provides some pythonic ways to import, export, manage documents and compute the term document matrics."
)
