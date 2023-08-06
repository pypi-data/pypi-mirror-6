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
    name='chicken',
    version='0.1.0',
    description='The Chicken came in the egg',
    long_description=readme + '\n\n' + history,
    author='Kyle Kelley',
    author_email='rgbkrk@gmail.com',
    url='https://github.com/rgbkrk/chicken',
    packages=[
        'chicken',
    ],
    package_dir={'chicken': 'chicken'},
    include_package_data=True,
    install_requires=[
        'egg'
    ],
    license="BSD",
    zip_safe=False,
    keywords='chicken',
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
