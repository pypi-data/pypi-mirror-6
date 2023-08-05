# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt
from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='silva.app.photogallery',
      version=version,
      description="Display folders as photo galleries in Silva CMS",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='silva photo gallery',
      author='Sylvain Viollon',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silva.app.photogallery',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva', 'silva.app'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        'five.grok',
        'js.galleriffic',
        'setuptools',
        'silva.core.conf',
        'silva.core.interfaces',
        'silva.core.layout',
        'silva.core.services',
        'silva.core.views',
        'silva.fanstatic',
        'zope.component',
        'zope.publisher',
        ],
      )
