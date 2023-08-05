#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name="luxx_communication",
      version="0.1.4",
      description="Module for control of Omicron LuxX laser",
      author="Roman Kiselev",
      author_email="roman.kiselew@gmail.com",
      py_modules=["luxx_communication"],
      scripts=['bin/laser_info.py','bin/run_laser.py'],
      license="GNU GPL v3",
      url="https://pypi.python.org/pypi/luxx_communication/",
      platforms=["Linux", "Windows"],
      requires=["pyserial"],
      classifiers=[
              "Development Status :: 3 - Alpha",
              "Topic :: Scientific/Engineering :: Physics",
              "Topic :: System :: Hardware",
          ],
     )