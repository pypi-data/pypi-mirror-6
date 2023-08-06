#!/usr/bin/env python2
# -*-coding: utf-8 -*-
#  setup.py
# Author: Gabriel Hondet
# Purpose: setup
# Created: 2014-04-18
#  
#  Copyright 2014 Gabriel Hondet <gabrielhondet@gmail.com>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README') as f:
    long_description = f.read()
with open('CHANGES') as c:
    changes = c.read()

setup(
    name='EweeStats',
    version='0.0dev3',
    description='Program to read, process, present and broadcast datas from sensors',
    author='Gabriel Hondet',
    author_email="gabrielhondet@gmail.com",
    license='Apache License, Version 2.0',
    url='https://pypi.python.org/pypi/EweeStats/',
    long_description=long_description + changes,
    platforms="GNU/Linux",
    packages=['EweeStats'],
    include_package_data=True,
    install_requires=['pyFirmata', 'pygal', 'pyserial', 'lxml'],
    extras_require = {
        'Excel': ['xlwt'],
        'ODF': ['ezodf2'],
        }
    )
