#!/usr/bin/python
# -*- coding: utf-8 -*-

class WeixinException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        try:
            return repr(self.msg)
        except Exception,e:
            return e

class TokenExpireException(WeixinException): pass
