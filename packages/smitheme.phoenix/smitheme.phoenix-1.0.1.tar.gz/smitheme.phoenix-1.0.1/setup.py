# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# $Id$

from setuptools import setup, find_packages
import os

version = '1.0.1'

setup(name='smitheme.phoenix',
      version=version,
      description="SMI Skin for Silva 2.3",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='skin silva smi',
      author='Gert Hengeveld',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/smitheme.phoenix',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['smitheme'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'silva.core.layout',
          'silva.core.views',
          'silva.core.conf',
          'silva.core.smi',
          'silva.resourceinclude'
      ],
      )
