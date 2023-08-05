# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '2.3.2'

tests_require = [
    'Products.Silva [test]',
    ]

setup(name='silva.core.layout',
      version=version,
      description="Layout system for Silva base on Zope Tool Kit and Grok",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='layout silva core',
      author='Infrae',
      author_email='info@infrae.com',
      url='http://infrae.com/products/silva',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva', 'silva.core'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Products.Silva',
          'five.grok',
          'five.localsitemanager',
          'grokcore.view',
          'infrae.layout',
          'martian',
          'setuptools',
          'silva.core.conf',
          'silva.core.interfaces',
          'silva.core.services',
          'silva.core.views',
          'silva.resourceinclude',
          'zope.app.interface',
          'zope.cachedescriptors',
          'zope.component',
          'zope.configuration',
          'zope.container',
          'zope.event',
          'zope.interface',
          'zope.intid',
          'zope.location',
          'zope.publisher',
          'zope.security',
          'zope.traversing',
          ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
