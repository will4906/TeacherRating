# -*- coding: utf-8 -*-
"""
Created on 2017/3/19

@author: will4906
"""


class Result:

    OK = 'ok'
    ERR = 'err'

    def __init__(self, result=OK, errMsg=None, parm=None):
        self.result = result
        self.errMsg = errMsg
        self.parm = parm