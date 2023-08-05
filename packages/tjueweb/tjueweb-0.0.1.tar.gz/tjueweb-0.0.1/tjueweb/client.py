#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
 @author:   hty0807@gmail.com
"""
from httputils import WebClient
from format import fmtattr
from pattern import extract
import re

class EWebClient():

    def __init__(self):
        self.client = WebClient()

    ''' attempt to log in with specified authentication '''
    ''' returns true if succeed '''
    def login(self, uid, password):
        # logging in
        resp = self.client.request("http://e.tju.edu.cn/Main/logon.do", data={'uid':uid, 'password':password})
        # if logging is a success, page would contain uid
        if resp.find(uid) < 0:
            return False
        return True

    ''' destroy session '''
    def logoff(self):
        self.client.request("http://e.tju.edu.cn/Main/logoff.do")
        return True

    ''' fetch basic info for current user '''
    def userinfo(self):
        resp = self.client.request("http://e.tju.edu.cn/UserInfo/UserBasicInfo.do")
        info = {}
        for row in extract(resp, 'userinfo/rows'):
            attr = fmtattr(row['attr'], row['value'])
            info[attr[0]] = attr[1]
        return info

    ''' get a list of available terms '''
    def achvterms(self):
        resp = self.client.request("http://e.tju.edu.cn/Education/stuachv.do")
        return extract(resp, 'achv/terms')

    ''' get course info of specified term '''
    def achv(self, term):
        resp = self.client.request("http://e.tju.edu.cn/Education/stuachv.do?todo=display&term=%s" % term)
        return extract(resp, 'achv/courses')
