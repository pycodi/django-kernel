#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()

setup(
    name='django-kernel',
    version='0.1',
    description="""Kenrel Model for Django""",
    long_description=readme + '\n\n',
    author='Nikita Kryuchkov',
    author_email='info@pycode.net',
    url='https://github.com/pycodi/django-kernel',
    packages=[
        'kernel',
    ],
    include_package_data=True,
    install_requires=[
        'Django>=1.9'
    ],
    license="MIT",
    zip_safe=False,
    keywords='django-kernel',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
