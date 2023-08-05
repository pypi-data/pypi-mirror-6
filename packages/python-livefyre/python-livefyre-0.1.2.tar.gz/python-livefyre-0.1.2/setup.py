#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


from setuptools import setup, find_packages

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='python-livefyre',
    version='0.1.2',
    description='API wrapper for Livefyre v3',
    long_description=readme + '\n\n' + history,
    author='Jason Novinger',
    author_email='jnovinger@gmail.com',
    url='https://github.com/jnovinger/python-livefyre',
    packages=find_packages(),
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
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
)
