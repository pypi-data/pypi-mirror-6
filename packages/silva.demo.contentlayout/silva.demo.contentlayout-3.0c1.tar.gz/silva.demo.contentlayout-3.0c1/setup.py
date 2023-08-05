# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt
from setuptools import setup, find_packages
import os

version = '3.0c1'

tests_require = [
    'Products.Silva [test]',
    ]

setup(name='silva.demo.contentlayout',
      version=version,
      description="Silva Content Layout demonstration templates",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silva.demo.contentlayout',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva', 'silva.demo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'five.grok',
          'setuptools',
          'silva.app.page',
          'silva.core.conf',
          'silva.core.contentlayout',
          'silva.core.interfaces',
          'silva.core.layout',
          'silva.fanstatic',
          'silva.translations',
          'silvatheme.standardissue',
          'zope.publisher',
          'zope.traversing',
      ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
