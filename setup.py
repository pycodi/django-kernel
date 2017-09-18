#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup




setup(
    name='django-kernel',
    version='0.3.0',
    description="""Kenrel Model for Django""",
    author='Nikita Kryuchkov',
    author_email='info@pycode.net',
    url='https://github.com/pycodi/django-kernel',
    packages=['kernel',],
    include_package_data=True,
    install_requires=[
        'Django>=1.9',
        'django-ckeditor',
        'django-stdimage',
        'django-templated-email',
        'django-import-export',
        'django-templated-email',
        'django-filter',
        'django-braces',
        'django-tables2',
        'djangorestframework>=3.6.4',
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
