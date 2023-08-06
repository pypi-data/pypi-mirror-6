# -*- coding=utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = 'JzStock',
    version = '0.2',
    keywords = ('Stock', 'Stock Tools'),
    description = 'JzStock is an elegant and simple Stock library for Python.',
    license = 'MIT License',
    install_requires = [], #['json>=2.0'],

    author = 'eric.ni',
    author_email = 'eric.ni@ijinzhuan.com',
    
    packages = find_packages(),
    platforms = 'any',
)