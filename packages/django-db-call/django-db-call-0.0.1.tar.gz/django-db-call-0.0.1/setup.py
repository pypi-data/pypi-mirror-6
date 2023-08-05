# -*- coding: utf-8 -*-
"""
django-db-call

Copyright (c) 2014, Friedrich Paetzke (f.paetzke@gmail.com)
All rights reserved.

"""
from setuptools import setup, find_packages


setup(name='django-db-call',
      py_modules=['django-db-call'],
      description='',
      long_description=(open('README.rst').read()),
      version='0.0.1',
      license='BSD',
      author='Friedrich Paetzke',
      author_email='f.paetzke@gmail.com',
      url='https://github.com/paetzke/django-db-call',
      packages=find_packages(exclude=['tests*']),
      classifiers=[
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Topic :: Software Development :: Libraries',
          'Topic :: Utilities',
      ])
