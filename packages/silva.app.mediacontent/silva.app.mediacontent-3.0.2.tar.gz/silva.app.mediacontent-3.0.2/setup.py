# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from setuptools import setup, find_packages
import os

def read_file(path):
    fd = open(path, 'r')
    try:
        return fd.read()
    finally:
        fd.close()


version = '3.0.2'

tests_require = [
    'Products.Silva [test]',
    'silva.core.contentlayout [test]']

setup(name='silva.app.mediacontent',
      version=version,
      description="Media content types for Silva CMS",
      long_description=read_file("README.txt") + "\n" +
                       read_file(os.path.join("docs", "HISTORY.txt")),
      classifiers=[
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Zope Public License",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Zope2",
          ],
      keywords='media silva infrae',
      author='Antonin Amand',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silva.app.mediacontent',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva', 'silva.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Products.Silva',
        'five.grok',
        'setuptools',
        'silva.core.conf',
        'silva.core.contentlayout',
        'silva.core.editor',
        'silva.core.interfaces',
        'silva.core.references',
        'silva.core.views',
        'silva.fanstatic',
        'silva.translations',
        'zeam.form.silva',
        'zope.component',
        'zope.event',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.publisher',
        'zope.schema',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
