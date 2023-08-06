#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
    EweeStats
    ~~~~~~~~~
    
    :copyright: Copyright 2014 Gabriel Hondet <gabrielhondet@gmail.com>
    :license: Apache 2.0, see LICENSE for details
"""

import os
import sys

__version__ = '0.0dev2'

#Check python version
if sys.version_info[:2] < (2, 7):
    raise ImportError('EweeStats requires Python version 2.7 or above')

print('Init done')
