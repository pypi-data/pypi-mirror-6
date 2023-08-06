#!/usr/bin/env python

from setuptools import setup
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='mkcss',
      version='0.1.0',
      description='A CSS generation thing.',
      long_description=read("README.rst"),
      author='Juhani Imberg',
      author_email='juhani@imberg.com',
      url='http://github.com/JuhaniImberg/mkcss/',
      license='MIT',
      packages=['mkcss'],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.2",
          "Programming Language :: Python :: 3.3",
      ],
      use_2to3=True)
