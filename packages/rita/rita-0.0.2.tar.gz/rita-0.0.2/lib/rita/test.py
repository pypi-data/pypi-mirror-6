# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unittest import TestCase 

class DummySession():
    def __init__(self):
        self.sessionid = "--"
    
    def __getitem__(self, name):
        return ""

    def __setitem__(self, name, value):
        pass

class BaseTestCase(TestCase):
    def open(self, app, url, params):
        def dummy_response(status, headers):
            pass

        import urllib
        try:
            from io import BytesIO
            input = BytesIO(urllib.parse.urlencode(params).encode("utf8"))
        except:
            from io import StringIO
            params = dict((k, v.encode("utf-8")) for k, v in params.items())
            input = BytesIO(urllib.urlencode(params))

        env = {"wsgi.input":input
               , "PATH_INFO":url
               , "REQUEST_METHOD": "POST"
               }
        ret = app._application(env, dummy_response)

    def assertTargetNotModified(self):
        print("-")

    def assertNotRedirected(self, app):
        self.assertTrue(not hasattr(app, "_redirectUrlForTest"), "必要のないリダイレクトが発生している") 

    def assertRedirected(self, app, location):
        self.assertTrue(hasattr(app, "_redirectUrlForTest") and app._redirectUrlForTest == location, "%sへのリダイレクトがされてない" % location)

    def assertNoFormError(self, app):
        for field in app.fields:
            self.assertEqual(len(app.form[field].errors), 0, "%sに入力エラーがある" % field)
