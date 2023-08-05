# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '1.3'

tests_require = [
    'Products.Silva [test]',
    ]

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
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Products.Formulator',
        'five.grok',
        'setuptools',
        'silva.core.services',
        'silva.translations',
        'skimpyGimpy',
        'zeam.form.base',
        'zeam.form.ztk',
        'zope.component',
        'zope.interface',
        'zope.schema',
        'zope.traversing',
        ],
      entry_points="""
      # -*- Entry points: -*-
      [zeam.form.components]
      captcha = silva.captcha.zeamform:register
      """,
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
