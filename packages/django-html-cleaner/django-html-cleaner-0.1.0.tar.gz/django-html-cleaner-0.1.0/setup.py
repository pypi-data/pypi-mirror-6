#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

import os
import sys
import django_html_cleaner

version = django_html_cleaner.__version__
readme = open('README.md').read()

# if sys.argv[-1] == 'publish':
#     os.system('python setup.py sdist upload')
#     print("You probably want to also tag the version now:")
#     print("  git tag -a %s -m 'version %s'" % (version, version))
#     print("  git push --tags")
#     sys.exit()

setup(
    name='django-html-cleaner',
    version=version,
    packages=['django_html_cleaner'],
    description="""Django text and character fields that clean HTML input.""",
    license="Public Domain / CC0",
    long_description=readme,
    author='Clinton Dreisbach',
    author_email='clinton.dreisbach@cfpb.gov',
    url='https://github.com/cndreisbach/django-html-cleaner',
)
