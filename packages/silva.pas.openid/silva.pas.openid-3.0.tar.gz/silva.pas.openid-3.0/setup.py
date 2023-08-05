# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '3.0'

setup(name='silva.pas.openid',
      version=version,
      description="OpenID suport for Silva CMS",
      long_description= open('README.txt').read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        ],
      keywords='pas openid silva',
      author='Sylvain Viollon',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silva.pas.openid',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['silva', 'silva.pas'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        "python-openid >= 2.1",
        "five.grok",
        "silva.core.interfaces",
        "silva.core.conf",
        "silva.core.views",
        "silva.core.services",
        "silva.pas.base",
        "silva.pas.membership",
        "silva.captcha",
        "setuptools",
        "zope.component",
        "zope.interface",
        "zope.publisher"],
      )
