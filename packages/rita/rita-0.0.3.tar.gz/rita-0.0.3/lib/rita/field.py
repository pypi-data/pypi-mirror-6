# -*- coding: utf-8 -*-
import cgi

class Field:
    def __init__(self, name, validators=None):
        self.name = name
        if validators == None:
            validators = []
        self.validators = validators
        
    def html_escape(self, s):
        if s == None or not isinstance(s, str):
            return s
        return cgi.escape(s, True).replace("'", "&#39;")

class TextField(Field):
    def __init__(self, name, validators=None):
        Field.__init__(self, name, validators)
    
    def render(self, name, value, readonly=False, opt=None):
        if readonly:
            return """%(value)s<input type="hidden" name="%(name)s" value="%(value)s"/>""" % {"name":name, "value":self.html_escape(value)}
        else:
            return """<input type="text" id="c_%(name)s" name="%(name)s" value="%(value)s"/>""" % {"name":name, "value":self.html_escape(value)}

class TextAreaField(Field):
    def __init__(self, name, validators=None):
        Field.__init__(self, name, validators)

    def render(self, name, value, readonly=False, opt=None):
        if readonly:
            return """%(display_value)s<input type="hidden" name="%(name)s" value="%(value)s"/>""" % {"display_value":self.html_escape(value).replace("\n", "<br/>"), "name":name, "value":self.html_escape(value)}
        else:
            return """<textarea id="c_%(name)s" name="%(name)s">%(value)s</textarea>""" % {"name":name, "value":self.html_escape(value)}

#TODO: DropDownListField,CheckBoxField,RadioButtonField,DateField,DateTimeField
