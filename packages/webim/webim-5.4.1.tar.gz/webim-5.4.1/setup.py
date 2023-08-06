#!/usr/bin/env python

from setuptools import setup

import webim

NAME = "webim"
PACKAGE = "webim"
VERSION = webim.__version__
AUTHOR = webim.__author__
DESCRIPTION = open("README.md").read()

setup(name=NAME,
      version=VERSION,
      description="Python webim client for nextalk.im",
      long_description=DESCRIPTION,
      author=AUTHOR,
      author_email="ery.lee@gmail.com",
      license="BSD",
      maintainer="Ery Lee",
      maintainer_email="ery.lee@gmail.com",
      url="http://github.com/webim/webim-python",
      download_url="http://github.com/webim/webim-python",
      packages=["webim"],
      package_dir={"webim": "webim"},
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ]
)

