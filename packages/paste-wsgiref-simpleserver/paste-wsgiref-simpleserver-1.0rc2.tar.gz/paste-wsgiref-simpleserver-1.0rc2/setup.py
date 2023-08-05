# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013, 2degrees Limited.
# All Rights Reserved.
#
# This file is part of paste-wsgiref-simpleserver
# <https://github.com/2degrees/paste-wsgiref-simpleserver>, which is subject
# to the provisions of the BSD at
# <http://dev.2degreesnetwork.com/p/2degrees-license.html>. A copy of the
# license should accompany this distribution. THIS SOFTWARE IS PROVIDED "AS IS"
# AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
version = open(os.path.join(here, 'VERSION.txt')).readline().rstrip()


setup(
    name='paste-wsgiref-simpleserver',
    version=version,
    description=
        'Paste plugin to make wsgiref.simple_server available as a server runner',
    long_description=README,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Paste',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        ],
    keywords='wsgi paste wsgiref single-threaded',
    author='2degrees Limited',
    author_email='2degrees-floss@googlegroups.com',
    url='http://pythonhosted.org/paste-wsgiref-simpleserver/',
    license='BSD (http://dev.2degreesnetwork.com/p/2degrees-license.html)',
    py_modules=['paste_wsgiref_simpleserver'],
    install_requires=[
        'PasteDeploy',
        ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.server_runner]
      wsgiref.simple_server = paste_wsgiref_simpleserver:run_simple_server
      """,
    )
