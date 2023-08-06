#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = 'Feedjack',
    version = '0.9.19',
    url = 'http://www.feedjack.org/',
    author = 'Gustavo Picón',
    author_email = 'gpicon@gmail.com',
    maintainer = "Domen Kozar",
    maintainer_email = "domen@dev.si",
    license = 'BSD',
    packages = find_packages(),
    install_requires=[
      'feedparser',
      'Django',
    ],
    entry_points="""
    [console_scripts]
    feedjack_update = feedjack.bin.feedjack_update:main
    """,
    zip_safe = False,
    description = 'Multisite Feed Agregator (Planet)',
    long_description = read('README.rst') + '\n\n' + read('CHANGES'),
)
