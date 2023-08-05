# -*- coding: utf-8 -*-
"""
django-orgco

Copyright (c) 2013-2014, Friedrich Paetzke (f.paetzke@gmail.com)
All rights reserved.

"""
from setuptools import setup, find_packages


setup(name='django-orgco',
      py_modules=['django_orgco'],
      description='django-orgco implements a template tag to use orgco easily in django templates',
      long_description=(open('README.rst').read()),
      packages=find_packages(exclude=['tests*']),
      version='0.1.0',
      license='BSD',
      author='Friedrich Paetzke',
      author_email='f.paetzke@gmail.com',
      url='https://github.com/paetzke/django-orgco',
      install_requires=open('requirements/package.txt').read().splitlines(),
      classifiers=[
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Software Development :: Libraries',
          'Topic :: Text Editors :: Emacs',
          'Topic :: Text Processing',
          'Topic :: Text Processing :: Markup',
      ])
