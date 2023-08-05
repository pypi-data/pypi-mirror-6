#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
 @author:   hty0807@gmail.com
"""
from handy import *

attrs = {'学号': ('id', STRIP), '姓名': ('name', STRIP), 
    '性别': ('gender', GENDER),
    '出生年月': ('bday', STRIP), '年级': ('year', STRIP), 
    '专业': ('major', STRIP), '班级': ('class', STRIP), 
    '身份证号': ('ssn', STRIP), '编号': ('id', STRIP), 
    '单位': ('depart', STRIP), '部门': ('staffroom', STRIP), 
    '办公电话': ('officetel', STRIP), '家庭电话': ('hometel', STRIP),
    '移动电话': ('mobile', STRIP), '电子邮件': ('email', STRIP)
}

def fmtattr(attr, val):
    if attr not in attrs:
        return attr, val
    entry = attrs[attr]
    return entry[0], entry[1](val)
