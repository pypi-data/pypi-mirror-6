#!/usr/bin/env python3

from distutils.core import setup

import tbar

setup(name = "tbar",
      version = tbar.__version__,
      description = "Visualize values with ascii characters in terminal",
      long_description = tbar.__doc__,
      author = "10sr",
      author_email = "sr10@sourceforge.org",
      url = "https://github.com/10sr/tbar",
      download_url = "https://github.com/10sr/tbar/archive/master.zip",
      packages = ["tbar"],
      scripts = ["bin/tbar"],
      keywords = "utility, terminal",
      classifiers = [
          "Topic :: Terminals",
          "Topic :: Utilities",
          "Environment :: Console",
          # "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
          "Intended Audience :: End Users/Desktop",
          "Programming Language :: Python :: 3.2",
          "Programming Language :: Python :: 3.3",
          "License :: Public Domain"
          ],
      license = "Public Domain"
      )
