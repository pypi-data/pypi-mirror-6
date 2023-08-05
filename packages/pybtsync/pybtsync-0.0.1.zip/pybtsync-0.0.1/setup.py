#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name = "pybtsync",
    version = "0.0.1",
    description = "A Python module for the BitTorrent Sync API.",
    long_description = open('README.rst').readline(),
    author = "Tiago Macarios",
    author_email = "tiagomacarios <at> the google email",
    url = "https://github.com/tiagomacarios/pybtsync",
    download_url = "https://github.com/tiagomacarios/pybtsync",
    packages = ['pybtsync',
                ],
    install_requires = ["requests"],
    license = open('LICENSE').readline(),
    keywords = "bittorrent sync api",
    classifiers = [ "Development Status :: 3 - Alpha",
                    "Environment :: Console",
                    "Intended Audience :: Developers",
                    "License :: OSI Approved :: MIT License",
                    "Natural Language :: English",
                    "Operating System :: OS Independent",
                    "Programming Language :: Python",
                    "Topic :: Internet",
                    "Topic :: Software Development",
                    "Topic :: Utilities",
                    ] # https://pypi.python.org/pypi?%3Aaction=list_classifiers                    
)
