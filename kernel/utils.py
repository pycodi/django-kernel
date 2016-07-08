# -*- coding: utf-8 -*-
from slugify import slugify as aw_slugify

__author__ = 'pyCode'


def slugify(str):
    return aw_slugify(str.lower())
