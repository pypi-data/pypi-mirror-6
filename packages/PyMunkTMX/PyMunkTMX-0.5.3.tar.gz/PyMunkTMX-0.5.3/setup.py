#!/usr/bin/env python
#encoding: utf-8

from setuptools import setup
import os
import pymunktmx


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name="PyMunkTMX",
      version=pymunktmx.__version__,
      description=pymunktmx.__description__,
      author=pymunktmx.__author__,
      author_email=pymunktmx.__author_email__,
      packages=['pymunktmx'],
      install_requires=['pymunktmx',
                        'pytmx',
                        'pygame>=1.9',
                        'pymunk>=4.0.0'],
      license="LGPLv3",
      url="https://github.com/wkmanire/PyMunkTMX",
      long_description="bumped the version number.",
      package_data={
          'pymunktmx': ['LICENSE', 'README.md']},
      classifiers=[
          "Intended Audience :: Developers",
          "Development Status :: 4 - Beta",
          "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
          "Programming Language :: Python :: 2.7",
          "Topic :: Games/Entertainment",
          "Topic :: Software Development :: Libraries :: pygame",
      ],
)
