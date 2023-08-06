# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Flask-Velox
-----------

Velox is a set of classes & mixins to help rapidly build Flask applications.
"""

import os
import sys

from setuptools import setup, find_packages


# Get current directory where setup is running
try:
    SETUP_DIRNAME = os.path.dirname(__file__)
except NameError:
    SETUP_DIRNAME = os.path.dirname(sys.argv[0])

# Change directory
if SETUP_DIRNAME != '':
    os.chdir(SETUP_DIRNAME)

# Paths to requirement files
INSTALL_DEPS = os.path.join('dependencies', 'install.txt')
TEST_DEPS = os.path.join('dependencies', 'test.txt')
DEV_DEPS = os.path.join('dependencies', 'dev.txt')


def read_dependencies(filename):
    """
    Read requirements file and process them into a list
    fpr usage in the setup function

    :param filename: Path to the file to read line by line
    :type filename: string

    :returns: list -- list of requirements
    """

    dependencies = []
    with open(filename) as f:
        for line in f.readlines():
            if not line or line.startswith('#'):
                continue
            dependencies.append(line.strip())
    return dependencies


def read(name):
    """
    Read file in local current working directory and return the contents

    :param name: The name of the file
    :type name: string

    :returns: string -- Contents of file
    """

    return open(name).read()


# Setup function
setup(
    name='Flask-Velox',
    version=read('VERSION').strip(),
    author='SOON_',
    author_email='dorks@thisissoon.com',
    url='https://github.com/thisissoon/Flask-Velox',
    description='Velox is a set of classes & mixins to help rapidly build '
                'Flask applications.',
    long_description=read('README.rst'),
    packages=find_packages(
        exclude=[
            "tests"]),
    include_package_data=True,
    zip_safe=False,
    # Dependencies
    install_requires=read_dependencies(INSTALL_DEPS),
    extras_require={
        'test': read_dependencies(TEST_DEPS),
        'develop': read_dependencies(DEV_DEPS)},
    # Dependencies not hosted on PyPi
    dependency_links=[],
    # Classifiers for Package Indexing
    # Entry points, for example Flask-Script
    entry_points={},
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'])
