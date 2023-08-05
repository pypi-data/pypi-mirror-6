# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt
from setuptools import setup, find_packages
import os

version = '1.0.2'

setup(name='silvatheme.silvadocs',
      version=version,
      description="Silva Docs theme for Silva CMS",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silvatheme silvadocs',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silvatheme.silvadocs',
      license='BSD and Creative Commons',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['silvatheme'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'grokcore.chameleon',
          'silva.core.conf',
          'silva.core.interfaces',
          'silva.core.layout',
          'zope.cachedescriptors',
          'zope.traversing',
          ],
      )
