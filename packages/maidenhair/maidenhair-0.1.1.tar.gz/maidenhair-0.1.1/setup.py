#!/usr/bin/env python
# coding=utf-8
"""
maidenhair

A plugin based data load library

(C) 2013 hashnote.net, Alisue
"""
name = 'maidenhair'
version = '0.1.1'
author = 'Alisue'
author_email = 'lambdalisue@hashnote.net'

import os
from setuptools import setup, find_packages

def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filename):
        return open(os.path.join(os.path.dirname(__file__), filename)).read()
    return __doc__

setup(
    name=name,
    version=version,
    description = "A plugin based data load library",
    long_description=read('README.rst'),
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
    keywords = "",
    author = "Alisue",
    author_email = "lambdalisue@hashnote.net",
    url=r"https://github.com/lambdalisue/maidenhair",
    download_url = (
        r"https://github.com/lambdalisue/maidenhair/tarball/master"),
    license = 'MIT',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    exclude_package_data = {'': ['README.txt']},
    zip_safe = True,
    install_requires=[
        'setuptools',
        'natsort',
        'bunch',
        'numpydoc',
    ],
)
