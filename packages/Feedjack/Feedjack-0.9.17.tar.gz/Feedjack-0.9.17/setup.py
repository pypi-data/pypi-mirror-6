#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages
from finddata import find_package_data


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = 'Feedjack',
    version = '0.9.17',
    url = 'http://www.feedjack.org/',
    author = 'Gustavo Picón',
    author_email = 'gpicon@gmail.com',
    maintainer = "Domen Kozar",
    maintainer_email = "domen@dev.si",
    license = 'BSD',
    packages = find_packages(),
    package_data = find_package_data(where='feedjack', package='feedjack'),
    scripts = ['feedjack/bin/feedjack_update.py'],
    install_requires=[
      'feedparser',
      'Django',
    ],
    zip_safe = False,
    description = 'Multisite Feed Agregator (Planet)',
    long_description = read('README.rst') + '\n\n' + read('CHANGES'),
)
