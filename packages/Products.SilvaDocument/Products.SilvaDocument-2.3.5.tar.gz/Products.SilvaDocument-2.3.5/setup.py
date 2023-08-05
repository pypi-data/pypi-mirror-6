# -*- coding: utf-8 -*-
# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '2.3.5'

tests_require = [
    'Products.Silva [test]',
    ]

setup(name='Products.SilvaDocument',
      version=version,
      description="Document content type for Silva 2",
      long_description=open(os.path.join("Products", "SilvaDocument", "README.txt")).read() + "\n" +
                       open(os.path.join("Products", "SilvaDocument", "HISTORY.txt")).read(),
      classifiers=[
              "Framework :: Zope2",
              "License :: OSI Approved :: BSD License",
              "Programming Language :: Python",
              "Topic :: Software Development :: Libraries :: Python Modules",
              ],
      keywords='silva cms document zope',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/Products.SilvaDocument',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Products.ParsedXML',
        'Products.Silva',
        'Products.SilvaExternalSources',
        'Products.SilvaKupu',
        'Sprout',
        'five.grok',
        'setuptools',
        'silva.core.conf',
        'silva.core.interfaces',
        'silva.core.references',
        'silva.core.services',
        'silva.core.smi',
        'silva.core.views',
        'silva.translations',
        'zeam.form.silva',
        'zope.component',
        'zope.event',
        'zope.interface',
        'zope.intid',
        'zope.traversing',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
