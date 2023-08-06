#!/usr/bin/env python
from setuptools import setup

setup(
      name='xms_sdk',
      version='1.0',
      description='The SDK used to interact with XMS.',
      packages=['sdk'],
      install_requires = ['python-dateutil']
)
