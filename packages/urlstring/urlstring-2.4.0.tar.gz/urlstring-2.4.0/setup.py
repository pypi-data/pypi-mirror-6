#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='urlstring',
    version='2.4.0',
    description='A fork of Zachary Voase\'s "URLObject" utility class for manipulating URLs.',
    author='Alexander Bohn',
    author_email='fish2000@gmail.com',
    url='http://github.com/fish2000/urlobject',
    packages=find_packages(exclude=('test',)),
)
