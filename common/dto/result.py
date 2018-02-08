# -*- coding: utf-8 -*-
"""
Created on 2017/3/19

@author: will4906
"""


class Result:

    def __init__(self, result='ok', errMsg=None, parm=None):
        self.result = result
        self.errMsg = errMsg
        self.parm = parm