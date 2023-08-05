# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
from setuptools import setup, find_packages
import os

version = '3.0'

tests_require = [
    'Products.Silva [test]',
    'Products.ZSQLiteDA',
    ]

setup(name='Products.SilvaPoll',
      version=version,
      description="Poll extension for Silva CMS",
      long_description=open(os.path.join("Products", "SilvaPoll", "README.txt")).read() + "\n" +
                       open(os.path.join("Products", "SilvaPoll", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
              "Framework :: Zope2",
              "License :: OSI Approved :: BSD License",
              "Programming Language :: Python",
              "Topic :: Software Development :: Libraries :: Python Modules",
              ],
      keywords='poll silva zope2',
      author='Guido Wesdorp, Wim Boucquaert, Jasper Op De Coul',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/Products.SilvaPoll',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Products.Formulator',
        'Products.Silva',
        'Products.SilvaExternalSources',
        'five.grok',
        'grokcore.chameleon',
        'setuptools',
        'silva.core.conf',
        'silva.core.interfaces',
        'silva.core.services',
        'silva.core.smi',
        'silva.core.views',
        'silva.fanstatic',
        'z3locales',
        'zeam.form.silva',
        'zope.component',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.publisher',
        'zope.schema',
        'zope.traversing',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require,}
      )
