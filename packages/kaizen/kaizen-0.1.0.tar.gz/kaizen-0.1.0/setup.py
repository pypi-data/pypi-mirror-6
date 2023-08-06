#!/usr/bin/env python
from setuptools import setup

with open("README", "r") as readme_file:
  readme = readme_file.read()

setup(
  name = "kaizen",
  version = "0.1.0",
  description = "A python client and cli for AgileZen API",
  long_description = readme,
  packages = ["kaizen"],
  author = "Bertrand Vidal",
  author_email = "vidal.bertrand@gmail.com",
  classifiers = [
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: Information Technology",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
  ],
)
