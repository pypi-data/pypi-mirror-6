#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from setuptools import setup

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='mts',
    version='0.2.1',
    description='Miratuserie.tv on the command line',
    long_description=readme + '\n\n' + history,
    author='Martín Gaitán',
    author_email='gaitan@gmail.com',
    url='https://github.com/mgaitan/mts',
    packages=[
        'mts', 'mts/orm_magic'
    ],
    package_dir={'mts': 'mts'},
    include_package_data=True,
    install_requires=['django', 'requests', 'docopt'],
    license="BSD",
    zip_safe=False,
    keywords='mts',
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
    entry_points = {
        'console_scripts': [
            'mts = mts:main',
            ]
        }

)
