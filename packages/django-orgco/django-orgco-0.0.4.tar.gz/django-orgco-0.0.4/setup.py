"""
django-orgco

Copyright (c) 2013, Friedrich Paetzke (f.paetzke@gmail.com)
All rights reserved.

"""
import os

from setuptools import setup, find_packages


pathname = os.path.abspath(os.path.dirname(__file__))
try:
    from orgco import convert_rst

    with open(os.path.join(pathname, 'README.org')) as org_file:
        with open(os.path.join(pathname, 'README.rst'), 'w') as rst_file:
            rst_file.write(convert_rst(org_file.read()))
except:
    print('Error converting .org')


setup(name='django-orgco',
      py_modules=['django_orgco'],
      description='django-orgco implements a template tag to use orgco easily in django templates',
      long_description=(open('README.rst').read()),
      packages=find_packages(exclude=['test*']),
      version='0.0.4',
      license='BSD',
      author='Friedrich Paetzke',
      author_email='f.paetzke@gmail.com',
      url='https://github.com/paetzke/django-orgco',
      install_requires=[
          'django',
          'orgco >= 0.0.9',
      ],
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
          'Topic :: Software Development :: Libraries',
          'Topic :: Text Editors :: Emacs',
          'Topic :: Text Processing',
          'Topic :: Text Processing :: Markup',
      ])
