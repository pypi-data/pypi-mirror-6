# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from setuptools import setup, find_packages
import os

version = '3.0'

tests_require = [
    'Products.Silva [test]',
    ]

setup(name='silva.export.html',
      version=version,
      description="Export Silva content to standalone HTML",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silva export html',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silva.export.html',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva', 'silva.export'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'five.grok',
        'setuptools',
        'silva.core.interfaces',
        'silva.core.layout',
        'silva.core.references',
        'silva.core.services',
        'silva.core.views',
        'silva.translations',
        'zope.component',
        'zope.interface',
        'zope.schema',
        'zope.publisher',
        'zope.traversing',
        ],
      tests_require=tests_require,
      extras_require={'test': tests_require},
      )
