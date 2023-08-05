#!/usr/bin/env python
import os
import sys

import setuptools

import graphmaster

with open('README.rst') as stream:
    readme = stream.read()

with open('HISTORY.rst') as stream:
    history = stream.read()

with open('LICENSE') as stream:
    license = stream.read()

setuptools.setup(
    name='graphmaster',
    version=graphmaster.__version__,
    description="Doesn't do anything yet.",
    long_description=readme + '\n\n' + history,
    author='Mike Stringer',
    author_email='mike.stringer@datascopeanalytics.com',
    url='https://github.com/stringertheory/graphmaster5000',
    license=license,
    packages=setuptools.find_packages(exclude=['tests*']),
    include_package_data=True,
)
