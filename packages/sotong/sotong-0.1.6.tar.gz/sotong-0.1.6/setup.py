#!/usr/bin/env python

import sys

from setuptools import setup, find_packages
import sotong


long_description = """
Sotong %s

%s
""" % (sotong.__version__, sotong.__doc__.strip())

setup(
    name='sotong',
    version=sotong.__version__,
    description='Tiny automation tool like Jenkins, Buildbot, etc...',
    long_description=long_description,
    author=sotong.__author__,
    packages=find_packages(),
    install_requires=['Fabric>=1.8.0',
                      'watchdog>=0.6.0'],
)
