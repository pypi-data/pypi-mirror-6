#!/usr/bin/env python

from setuptools import setup

setup(
  name             = "prebuild.py",
  version          = "0.0.1",
  description      = "Python CLI for prebuild.me",
  long_description = "Python CLI for prebuild.me",
  author           = "Brian Lauber",
  author_email     = "constructible.truth@gmail.com",
  scripts          = ["bin/prebuild.py"],
  packages         = ["prebuild"],

  license          = "MIT"
)
