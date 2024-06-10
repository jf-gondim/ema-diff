#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from skbuild import setup
from setuptools import find_packages

# Main setup configuration.
setup(packages=find_packages(),
      include_package_data=True,
      zip_safe=False)
