# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
from setuptools import setup, find_packages
import os

version = '3.0.2'

setup(name='silva.translations',
      version=version,
      description="Translations files in many languages for the Silva CMS",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silva translations',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silva.translations',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'collective.monkeypatcher',
          'infrae.wsgi',
          'setuptools',
          'zope.i18n',
          'zope.i18nmessageid',
          'zope.publisher',
          ],
      )
