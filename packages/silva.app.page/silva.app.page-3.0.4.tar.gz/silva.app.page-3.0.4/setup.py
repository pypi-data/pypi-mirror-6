# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
from setuptools import setup, find_packages
import os

version = '3.0.4'

tests_require = [
    'Products.Silva [test]',
    'silva.app.news',
    ]

setup(name='silva.app.page',
      version=version,
      description="Silva page content types for Silva CMS",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
          "Environment :: Web Environment",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Zope2",
        ],
      keywords='silva contentlayout zope cms',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silva.app.page',
      license='GPL',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva', 'silva.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'five.grok',
          'setuptools',
          'silva.core.conf',
          'silva.core.contentlayout',
          'silva.core.interfaces',
          'silva.core.views',
          'silva.core.xml',
          'silva.translations',
          'silva.ui',
          'zeam.form.silva',
          'zope.component',
          'zope.event',
          'zope.i18n',
          'zope.interface',
          'zope.lifecycleevent',
          ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
