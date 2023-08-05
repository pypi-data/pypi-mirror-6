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
    name='python-livefyre',
    version='0.1.0',
    description='API wrapper for Livefyre v3',
    long_description=readme + '\n\n' + history,
    author='Jason Novinger',
    author_email='jnovinger@gmail.com',
    url='https://github.com/jnovinger/python-livefyre',
    packages=[
        'python-livefyre',
    ],
    package_dir={'python-livefyre': 'livefyre'},
    include_package_data=True,
    install_requires=[
        'PyJWT>=0.1.6',
        'requests>=2.2.0',
    ],
    license="BSD",
    zip_safe=False,
    keywords='python-livefyre',
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
