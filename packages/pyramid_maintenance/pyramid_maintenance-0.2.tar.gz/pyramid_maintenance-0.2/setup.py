#! /usr/bin/env python
# -*- coding: utf-8 -*-

############################################################################
#
# Copyright © 2014 Benoît Pineau <beny@sickless.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the GNU Public License,
# Version 2.0 (GPL). A copy of the GPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################

import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    ]

setup(name='pyramid_maintenance',
      version='0.2',
      description='pyramid_maintenance',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Benoît Pineau',
      author_email='beny@sickless.net',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires + ['webtest', 'pyramid_mako'],
      test_suite="pyramid_maintenance",
      entry_points="""\
      [paste.app_factory]
      main = pyramid_maintenance:main
      """,
      )
