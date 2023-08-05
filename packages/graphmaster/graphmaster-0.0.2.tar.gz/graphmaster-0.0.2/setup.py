#!/usr/bin/env python
"""Packaging script for graphmaster. Most of the stuff in here is from:

https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/
"""
# standard library
import os
import sys

# 3rd party
import setuptools

# local (to use version)
import graphmaster

# use this to publish to pypi
if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload -r pypi")
    os.system("python setup.py bdist_wheel upload -r pypi")
    sys.exit()

# read these files to use later in the description
with open('README.rst') as stream:
    readme = stream.read()
with open('HISTORY.rst') as stream:
    history = stream.read()
with open('LICENSE') as stream:
    license = stream.read()

# do the bizness
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
