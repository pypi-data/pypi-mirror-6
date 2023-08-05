# -*- coding: utf-8 -*-
"""
consolor

Copyright (c) 2013, Friedrich Paetzke (f.paetzke@gmail.com)
All rights reserved.

"""
from setuptools import setup, find_packages


setup(name='consolor',
      py_modules=['consolor'],
      description='Consolor provides highlighting functions for terminals.',
      long_description=(open('README.rst').read()),
      version='0.1.1',
      author='Friedrich Paetzke',
      author_email='f.paetzke@gmail.com',
      license='BSD',
      url='https://github.com/paetzke/consolor',
      packages=find_packages(exclude=['tests*']),
      classifiers=[
          'Environment :: Console',
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
          'Topic :: Software Development :: User Interfaces',
          'Topic :: Terminals',
          'Topic :: Utilities',
      ])
