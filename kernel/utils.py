# -*- coding: utf-8 -*-
from slugify import slugify as aw_slugify

__author__ = 'pyCode'


def slugify(str):
    return aw_slugify(str.lower())


def upload_dir(instance, filename):
    return '{1}/{0}'.format(filename, str(instance.__class__.__name__).lower())
