#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name             = 'django-castor',
    version          = '0.2.1',
    author           = "Zachary Voase",
    author_email     = "z@zacharyvoase.com",
    url              = 'https://github.com/zacharyvoase/django-castor',
    description      = "A content-addressable storage backend for Django.",
    packages         = find_packages(where='.', exclude='test'),
)
