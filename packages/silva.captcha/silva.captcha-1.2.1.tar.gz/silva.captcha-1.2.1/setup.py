# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '1.2.1'

setup(name='silva.captcha',
      version=version,
      description="Captcha support for Silva",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        ],
      keywords='captcha silva',
      author='Sylvain Viollon',
      author_email='info@infrae.com',
      url='https://svn.infrae.com/silva.captcha/trunk',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['silva'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'collective.captcha',
        'silva.core.upgrade',
        ],
      )
