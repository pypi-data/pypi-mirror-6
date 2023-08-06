#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

__version__ = '0.1.0'
__author__  = 'Zeuxis Lo'
__email__   = 'seekstudio@gmail.com'

setup(
    name='qqsuperman',
    version=__version__,
    url='https://github.com/zeuxisoo/python-qqsuperman/',
    license='BSD',
    author=__author__,
    author_email=__email__,
    description='The short of descriptions',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=open('requirements.txt').read().splitlines(),
)
