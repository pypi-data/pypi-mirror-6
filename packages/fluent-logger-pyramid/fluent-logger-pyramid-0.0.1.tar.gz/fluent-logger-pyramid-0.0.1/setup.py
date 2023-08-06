#!/usr/bin/python

from os import path

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

README = path.abspath(path.join(path.dirname(__file__), 'README.md'))
desc = 'A Python logging handler for Fluentd, with better Pyramid integration'

setup(
  name='fluent-logger-pyramid',
  version='0.0.1',
  description=desc,
  long_description=open(README).read(),
  package_dir={'fluent': 'fluent'},
  packages=['fluent'],
  install_requires=['msgpack-python', 'simplejson'],
  author='Nash Yeung',
  author_email='nashyeung@gmail.com',
  url='https://github.com/nashyeung/fluent-logger-pyramid',
  download_url='http://pypi.python.org/pypi/fluent-logger-pyramid/',
  license='Apache License, Version 2.0',
  classifiers=[
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
  ],
  test_suite='tests'
)
