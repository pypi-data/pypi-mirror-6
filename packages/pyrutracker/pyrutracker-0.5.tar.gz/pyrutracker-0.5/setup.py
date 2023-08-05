#!/usr/bin/env python
# coding=utf-8

from setuptools import setup
from pyrutracker import __version__, __description__, requires, README


setup(name='pyrutracker',
      version=__version__,
      description=__description__,
      author='wistful',
      author_email='wst.public.mail@gmail.com',
      url="https://bitbucket.org/wistful/rutracker",
      license="MIT License",
      packages=['pyrutracker'],
      long_description=README,
      install_requires=requires,
      platforms=["Unix,"],
      keywords="html, parser, rutracker",
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: X11 Applications",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      )
