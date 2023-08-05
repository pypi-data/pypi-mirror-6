# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
from setuptools import setup, find_packages
import os

version = '1.5'

setup(name='silvatheme.standardissue',
      version=version,
      description="Standard Issue theme for Silva CMS",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silvatheme standardissue',
      author='Infrae - Design by NodeThirtyThree',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silvatheme.standardissue',
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
          'zeam.form.silva',
          'zope.cachedescriptors',
          'zope.traversing',
          ],
      )
