# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from sqlalchemy import Integer, String
class Validator:
    def __init__(self, _=None):
        if _ == None: #国際化対応
            _ = lambda x:x
        self._ = _
    
    @staticmethod
    def getDefaultValidators(_, dbtype):
        ret = []
        if isinstance(dbtype, Integer):
            ret.append(IntegerValidator(_))
        elif isinstance(dbtype, String):
            if dbtype.length != None:
                ret.append(MaxLengthValidator(dbtype.length, _))
        return ret

class RequiredValidator(Validator):
    def validate(self, name, value):
        result = value != "" and value != None
        if result:
            return []
        else:
            return [self._("%(name)sを入力してください。") % ({"name":name})]

#TODO 自然数バリデータも必要
class IntegerValidator(Validator):
    def validate(self, name, value):
        try:
            int(value)
            return []
        except ValueError:
            return [self._("%(name)sは数値で入力してください。") % ({"name":name})]

class MaxLengthValidator(Validator):
    def __init__(self, maxLength, _=None):
        Validator.__init__(self, _)
        self.maxLength = maxLength

    def validate(self, name, value):
        if len(value) <= self.maxLength: 
            return []
        else:
            return [self._("%(name)sは%(maxLength)s文字以内で入力してください。") % ({"name":name, "maxLength":self.maxLength})]
