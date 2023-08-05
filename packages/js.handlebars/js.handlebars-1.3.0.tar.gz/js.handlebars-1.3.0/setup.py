#!/usr/bin/python

import setuptools
from setuptools import find_packages

setuptools.setup(
  name = 'js.handlebars',
  version = '1.3.0',
  license = 'BSD',
  description = 'Fanstatic package for Handlebars.js',
  long_description = open('README.txt').read(),
  author = 'Matt Good',
  author_email = 'matt@matt-good.net',
  url = 'http://github.com/mgood/js.handlebars/',
  platforms = 'any',
  packages=find_packages(),
  namespace_packages=['js'],
  include_package_data=True,
  zip_safe = False,
  install_requires=[
    'fanstatic',
  ],
  setup_requires=[
    'setuptools-git',
  ],
  entry_points={
    'fanstatic.libraries': [
      'handlebars = js.handlebars:library',
    ],
  },
)
