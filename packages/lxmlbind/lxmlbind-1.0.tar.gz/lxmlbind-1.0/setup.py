#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from lxmlbind import __version__

__build__ = ""

readme = open("README.md").read()

setup(name="lxmlbind",
      version=__version__ + __build__,
      description="Python LXML object binding.",
      long_description=readme,
      author="Jesse Myers",
      author_email="jesse@locationlabs.com",
      url="https://github.com/jessemyers/lxmlbind",
      packages=find_packages(exclude=["*.tests"]),
      setup_requires=[
          "nose>=1.3.0",
      ],
      install_requires=[
          "lxml>=3.2.4",
      ],
      tests_require=[
      ],
      test_suite="lxmlbind.tests",
      )
