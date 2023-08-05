#!/usr/bin/env python

import os
import sys

from setuptools import setup


extra_requires = []
if sys.version_info[0:2] == (2, 6):
    extra_requires.append("ordereddict")

setup(name='toxgen',
      version='0.1',
      description='Tox.ini generator',
      author="Christophe de Vienne",
      author_email='cdevienne@gmail.com',
      url='https://bitbucket.org/cdevienne/toxgen',
      scripts=[
          'toxgen.py',
      ],
      install_requires=[
          'six>=1.4.1',
      ] + extra_requires,
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
      ],
      long_description=open('README.rst', 'rb').read(),
      keywords="tox template generator combinations test",
     )

