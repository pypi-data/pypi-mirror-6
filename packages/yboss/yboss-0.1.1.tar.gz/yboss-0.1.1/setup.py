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
    name='yboss',
    version='0.1.1',
    description='Python wrapper for Yahoo Boss API',
    long_description=readme + '\n\n' + history,
    author='Inovatho',
    author_email='inovacao@catho.com',
    url='https://github.com/inovatho/yboss',
    packages=[
        'yboss',
    ],
    package_dir={'yboss': 'yboss'},
    include_package_data=True,
    install_requires=[
        'requests', 'oauthlib'
    ],
    license="BSD",
    zip_safe=False,
    keywords='yboss',
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