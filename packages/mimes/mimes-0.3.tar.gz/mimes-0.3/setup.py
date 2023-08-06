#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='mimes',
    version='0.3',
    description=('Parses mimetype-strings (RFC 1049, 2045, 2047 and 2231) and '
                 'allows comparing these.'),
    long_description=read('README.rst'),
    author='Marc Brinkmann',
    author_email='git@marcbrinkmann.de',
    url='http://github.com/mbr/mimetypes',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    install_requires=['networkx'],
)
