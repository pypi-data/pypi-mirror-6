# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# $Id$

from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='silvatheme.multiflex',
      version=version,
      description="Multiflex Demo Skin for Silva CMS",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='skin silva',
      author='Wim Boucquaert',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silvatheme.multiflex',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['silvatheme'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
	  'silva.core.layout',
          'silva.core.views',
          'silva.core.conf',
          'zope.cachedescriptors',
      ],
      )
