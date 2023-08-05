# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from setuptools import setup, find_packages
import os

version = '3.0.2'

tests_require = [
    'Products.Silva [test]',
    ]

setup(name='silva.core.layout',
      version=version,
      description="Layout and theme engine for Silva CMS",
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
      url='https://github.com/silvacms/silva.core.layout',
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
          'grokcore.layout',
          'grokcore.view',
          'grokcore.viewlet',
          'infrae.wsgi',
          'js.jquery',
          'js.jqueryui',
          'martian',
          'setuptools',
          'silva.core.conf',
          'silva.core.interfaces',
          'silva.core.services',
          'silva.core.views',
          'silva.fanstatic',
          'silva.translations',
          'zeam.component',
          'zope.app.interface',
          'zope.cachedescriptors',
          'zope.component',
          'zope.configuration',
          'zope.container',
          'zope.event',
          'zope.i18n',
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
