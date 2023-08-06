#!/usr/bin/env python
from setuptools import setup

with open("README.md", "r") as readme_file:
  readme = readme_file.read()

setup(
  name = "kaizen",
  version = "0.1.1",
  description = "A python client and cli to manage your projects on AgileZen Kanban style.",
  long_description = readme,
  packages = ["kaizen"],
  author = "Bertrand Vidal",
  author_email = "vidal.bertrand@gmail.com",
  url = "https://pypi.python.org/pypi/kaizen",
  classifiers = [
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: Information Technology",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
  ],
  setup_requires = [
    "nose",
    "responses",
  ],
  install_requires = [
    "requests",
  ],
)
