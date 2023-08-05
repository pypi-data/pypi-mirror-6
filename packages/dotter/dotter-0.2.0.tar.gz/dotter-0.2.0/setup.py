# -*- coding: utf-8 -*-
"""
dotter

Copyright (c) 2013, Friedrich Paetzke (f.paetzke@gmail.com)
All rights reserved.

"""
from setuptools import setup, find_packages


setup(name='dotter',
      py_modules=['dotter'],
      description='Dotter is a graphviz wrapper for Python 2 and 3',
      long_description=(open('README.rst').read()),
      version='0.2.0',
      license='BSD',
      author='Friedrich Paetzke',
      author_email='f.paetzke@gmail.com',
      url='https://github.com/paetzke/dotter',
      packages=find_packages(exclude=['tests*']),
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Software Development :: Libraries',
          'Topic :: Utilities',
      ])
