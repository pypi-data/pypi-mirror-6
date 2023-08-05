#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='wikipediabase',
    version='0.1.0',
    description='"Wikipedia scraper done in python for use in start.mit.edu"',
    long_description=readme + '\n\n' + history,
    author='Chris Perivolaropoulos',
    author_email='darksaga2006@gmail.com',
    url='https://github.com/fakedrake/wikipediabase',
    packages=[
        'wikipediabase',
    ],
    package_dir={'wikipediabase': 'wikipediabase'},
    include_package_data=True,
    install_requires=[
        'sexpdata',
    ],
    license="BSD",
    zip_safe=False,
    keywords='wikipediabase',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)
