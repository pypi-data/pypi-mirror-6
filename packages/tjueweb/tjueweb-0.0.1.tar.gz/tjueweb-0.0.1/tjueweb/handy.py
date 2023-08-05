#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
 @author:   hty0807@gmail.com
"""

STRIP = lambda x: x.replace("&nbsp;", " ").strip()
NUMERIC = lambda x: float(STRIP(x))
GENDER = lambda x: 'Male' if STRIP(x) == '男' else 'Female'
