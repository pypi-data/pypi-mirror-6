#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import cms_saq

version = cms_saq.__version__

requires = [
    'beautifulsoup4>=4.3.1'
]

setup(
    name='django-cms-saq',
    version=version,
    description='Self-assessment questionnaires with Django CMS.',
    install_requires=requires,
    author='Maplecroft',
    author_email='james.rutherford@maplecroft.com',
    url='https://github.com/Maplecroft/django-cms-saq',
    packages=['cms_saq', 'cms_saq.migrations', 'cms_saq.management', 'cms_saq.management.commands', 'cms_saq.templatetags'],
    license='LICENSE.txt',
    include_package_data = True,
)
