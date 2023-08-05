# -*- coding: utf-8 -*-
# Copyright (c) 2012 Infrae. All rights reserved.x

from setuptools import setup, find_packages
import os

version = '3.0'

setup(name='smitheme.industrial',
      version=version,
      description="Alternate (original) SMI Skin for Silva 3.0",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='skin silva smi',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/smitheme.industrial',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['smitheme'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'five.grok',
          'js.jqueryui',
          'megrok.pagetemplate',
          'setuptools',
          'silva.core.conf',
          'silva.core.interfaces',
          'silva.ui',
          'zope.interface',
          'zope.publisher',
          ],
      )
