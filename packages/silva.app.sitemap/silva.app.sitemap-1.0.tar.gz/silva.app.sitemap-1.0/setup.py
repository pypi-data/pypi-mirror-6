# -*- coding: utf-8 -*-
# Copyright (c) 2002-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from setuptools import setup, find_packages
import os

version = '1.0'

tests_require = [
    'Products.Silva [test]',
    ]

setup(name='silva.app.sitemap',
      version=version,
      description="Generate XML Sitemaps for Silva CMS",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silva sitemap',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silva.app.sitemap',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva', 'silva.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'five.grok',
        'setuptools',
        'silva.core.conf',
        'silva.core.interfaces',
        'silva.core.services',
        'zeam.form.silva',
        'zope.component',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.schema',
        ],
      tests_require=tests_require,
      extras_require={'test': tests_require},
      )
