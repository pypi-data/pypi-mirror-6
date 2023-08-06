# -*- coding: utf-8 -*-
import sys
import cgi
import gettext
import unicodedata
import json
from io import BytesIO
from collections import OrderedDict

try:
    from mako.lookup import TemplateLookup
except:pass

try:
    from sqlalchemy import Integer
except:pass

try:
    from rita.validator import Validator
except:pass
from rita.session import HttpSession

STATUS_CODES = {200:"OK", 206:"Partial Content"
                , 301:"Moved Permanently"
                , 302:"Moved Temporarily"
                , 304:"Not Modified"
                , 400:"Bad Request"
                , 401:"Unauthorized", 403:"Forbidden"
                , 404:"Not Found", 500:"Internal Server Error"
                , 501 :"Not Implemented"
                , 503:"Service Unavailable"}

class _FinishResponseException(Exception):
    pass

class BaseController(object):
    def __init__(self):
        self.env = {}
        self.attr = {"page":self}
        self.charset = self.getCharSet()
        self.outputExpiredHeader = True

        self._headers = {}
        self._status = 200
        self._params = None
        self._fieldstorage = None
        self._output_buffer = BytesIO()
    
    def output(self, s):
        self._output_buffer.write(s.encode(self.charset))

    def status(self, code):
        self._status = code
        
    def header(self, name, value=None):
        #FIXME: nameはXxxx-Xxxxの形式に変換して統一すべきでは

        #valueが指定されていなければ現在の値を返す
        if value == None:
            if name in self._headers:
                return self._headers[name]
            else:
                return None
        
        #FIXME:正規表現でのホワイトリストチェックに変更
        if value.find("\r") != -1 or value.find("\n") != -1:
            raise ValueError("HTTP header must not contain control codes.")
        
        self._headers[name] = value       

    def redirect(self, location, finish_response=True, permit_external_site=False):
        """リダイレクトヘッダを出力する,finish_response=Trueならそれ以降の処理はしない
        (str,bool,bool) as void"""
        self.status(302)
        self.header("Location", location)
        if not permit_external_site:
            if len(location) > 2: #/から始まるURL以外のサイトにリダイレクトさせない
                #FIXME route.pyなどからのホワイトリスト対応の方がいいかも
                if not(location.startswith("/") and location[1] != "/"):
                    raise ValueError("redirect to external site is not permitted.")
        
        if finish_response:
            self.finishResponse()

    def finishResponse(self):
        raise _FinishResponseException()

    def FieldStorage(self):
        if self._fieldstorage != None:
            return self._fieldstorage

        ret = {}
        e = self.env.copy()
        
        if "CONTENT_TYPE" in e and e["CONTENT_TYPE"] == "application/json":
            ret = json.loads(self.env['wsgi.input'].read().decode(self.charset))
            if sys.version_info.major >= 3:
                ret = dict([(k, cgi.MiniFieldStorage(k, str(v))) for k, v in ret.items()])
            else:
                ret = dict([(k, cgi.MiniFieldStorage(k, str(v) if not isinstance(v, unicode) else v.encode(self.charset))) for k, v in ret.items()])
        else:
            if sys.version_info.major >= 3:
                ret = cgi.FieldStorage(fp=self.env['wsgi.input'], environ=e, keep_blank_values=1, encoding=self.charset)
            else:
                ret = cgi.FieldStorage(fp=self.env['wsgi.input'], environ=e, keep_blank_values=1)
            if ret.value == "":
                ret = {}
            
        self._fieldstorage = ret
        return ret
    
    def application(self, env, start_response):
        try:
            self.env = env
            self._initialize()
            self.initialize()
            self.auth()
            self._preprocess()
            self.process()
        except _FinishResponseException:
            pass
        finally:
            self.finalize()

        if self.header("Content-Type") == None: 
            if self.charset == "cp932":
                self.header("Content-Type", "text/html;charset=Shift_JIS")
            else:
                self.header("Content-Type", "text/html;charset=utf-8")

        if self.outputExpiredHeader:
            self.header("Pragma", "no-cache")
            self.header("Cache-Control", "no-cache")
            self.header("Expires", "-1")

        response_headers = [(x, str(self._headers[x])) for x in self._headers]
        start_response("%s %s" % (self._status, STATUS_CODES[self._status]), response_headers)
        ret = self._output_buffer.getvalue()
        self._output_buffer.close()
        return [ret]

    def _py2_i18n_helper(self, s):
        #python2系だとバイト型の文字列が渡される場合があるため
        if not isinstance(s, unicode):
            s = s.decode("utf8")  
        return gettext.Catalog("messages", self.getLocaleDir(), self.getLanguages(), fallback=True).gettext(s)
    
    def _initialize(self):
        self._params = self.FieldStorage()
        self.session = self.getHttpSession()
        self.currentUser = self.getCurrentUser()
        locale_dir = self.getLocaleDir()
        if locale_dir != None:
            if sys.version_info.major >= 3:
                self.attr["_"] = gettext.Catalog("messages", locale_dir, self.getLanguages(), fallback=True).gettext
            else:
                self.attr["_"] = self._py2_i18n_helper
        else:
            self.attr["_"] = lambda x:x

    def getLocaleDir(self):
        #国際化するならロケールデータが入ったディレクトリを返す
        pass

    def finalize(self):
        #必要あれば子クラスでオーバーライド
        pass        
    
    def getCharSet(self):
        #必要あれば子クラスでオーバーライド
        return "utf8"
    
    def getHttpSessionStore(self):
        #必要あれば子クラスでオーバーライド
        return {}
    
    def getHttpSession(self):
        #必要あれば子クラスでオーバーライド
        return HttpSession(self)

    def getDocumentRoot(self):
        #必要あれば子クラスでオーバーライド
        return "."
    
    def getCurrentUser(self):
        return None

    def getLanguages(self):
        return ["ja-jp"]

    def initialize(self):
        pass #アプリケーション側で必要に応じて実装する
    
    def auth(self):
        pass #アプリケーション側で必要に応じて実装する
    
    def _preprocess(self):
        pass #親クラスでは何もしない（フレームワーク内の継承先で必要に応じて実装する）

    def renderString(self, file_name=None):
        """テンプレートから文字列を生成する"""
        #モジュール名を解析
        modile_name = self.__module__
        folder = "/"
        if "." in modile_name:
            folder += modile_name[:modile_name.rfind(".")].replace(".", "/")
        if file_name == None:
            file_name = modile_name[modile_name.rfind(".") + 1:] + ".html"

        #テンプレートファイルを探す
        mylookup = None
        if sys.version_info.major >= 3:
            mylookup = TemplateLookup(directories=[self.getDocumentRoot() + folder], input_encoding="utf-8", default_filters=["h", "str"])
        else:
            default_filters = ["decode." + self.charset] + ["h"]
            mylookup = TemplateLookup(directories=[self.getDocumentRoot() + folder], input_encoding="utf-8", default_filters=default_filters)
        mytemplate = mylookup.get_template(file_name)

        return mytemplate.render_unicode(**self.attr)

    def render(self, file_name=None):
        """テンプレートから文字列を出力する"""
        self.output(self.renderString(file_name))
        
    def getParam(self, name, default=None):
        if name in self._params:
            param = self._params[name]
            if isinstance(param, cgi.FieldStorage):
                return param
            elif not isinstance(param, list):
                if sys.version_info.major >= 3:
                    return param.value
                else:
                    return param.value.decode(self.charset)
            else:
                ret = []
                for p in param:
                    ret.append(param.value)
                return ret
        return default

class _FormInput(object):
    def __init__(self, value):
        self.value = value
        #入力チェックが済んでいるかどうか
        self.checked = False
        self.errors = []

class FormState(object):
    INPUTTING = 10 #編集画面を開いている
    INPUT_CONFIRM = 11 #更新または追加の入力確認
    INPUT_READY = 12 #更新または追加の入力完了
    DELETE_CONFIRM = 21 #削除の入力確認
    DELETE_READY = 22 #削除の入力完了
    CANCELED = 100 #キャンセルされた

class BaseFormController(BaseController):
    FormState = FormState
    def __init__(self):
        super(BaseFormController, self).__init__()
        self.fields = OrderedDict()
        self.targetClass = None
        self.targetFieldNames = []
        
        self.showInputConfirm = False
        
        self._cached_target = None
        self._validation_result = None #validateメソッドを呼び出した結果のキャッシュ

    def _preprocess(self):
        self.form = {}
        for name in self.fields.keys():
            self.form[name] = _FormInput(self.getParam(name, ""))
        if not self.isPostBack():
            self._prepareForm()
            self.prepareForm()

    def getParam(self, name, default=None):
        ret = BaseController.getParam(self, name, default)
        #数値のフィールドの場合は全角数値は自動的に半角に変換する
        if self.targetClass != None:
            if name in self.fields:
                dbtype = self.targetClass.metadata.tables[self.targetClass.__tablename__].columns[name].type
                if isinstance(dbtype, Integer):
                    if sys.version_info.major >= 3:
                        try:
                            ret = int(ret)
                        except:
                            pass
                    else:
                        try:
                            ret = int(unicodedata.normalize('NFKC', ret))
                        except:
                            pass
        return ret

    def getDBSession(self):
        return None
    
    def getPrimaryKey(self):
        splited = str(self.env["PATH_INFO"]).split("/")
        try:
            return int(splited[-1])
        except:
            return None
            
    def getTargetWithSession(self):
        session = self.getDBSession()
        if self.targetClass != None:
            if self.getPrimaryKey() != None:
                return session, session.query(self.targetClass).filter(self.targetClass.id == int(self.getPrimaryKey()))[0]
        return session, None
    
    def getTarget(self, use_cache=True):
        if use_cache and self._cached_target != None:
            return self._cached_target
        session, ret = self.getTargetWithSession()
        self._cached_target = ret
        return ret
    
    def prepareForm(self):
        target = self.getTarget()
        if target != None:
            for field_name in self.targetFieldNames:
                self.form[field_name].value = getattr(target, field_name) 
    
    def _prepareForm(self):
        pass
    
    def _validateForm(self):
        #一度呼び出し済みなら結果のみを返す
        if self._validation_result != None:
            return self._validation_result

        if not self.isPostBack():return
        ret = True

        all_error_messages = []
        for field_name in self.fields:
            value = self.form[field_name].value
            dbtype = None
            if self.targetClass != None:
                dbtype = self.targetClass.metadata.tables[self.targetClass.__tablename__].columns[field_name].type
            #明示的に設定されたバリデータとDBスキーマでの入力チェック
            for validator in Validator.getDefaultValidators(self.attr["_"], dbtype) + self.fields[field_name].validators:
                error_messages = validator.validate(self.fields[field_name].name, value)
                self.form[field_name].errors += error_messages
                all_error_messages += error_messages
            
        if len(all_error_messages) != 0:
            ret = False

        ret = ret and self.validateForm()
        self._validation_result = ret #バリデーション結果をキャッシュ
        return ret

    def validateForm(self):
        return True #子クラスで実装
            
    def updateTarget(self, options=None, auto_commit=True):
        if options == None:options = {} 
        session, target = self.getTargetWithSession()
        if target == None:
            target = self.targetClass()
            session.add(target)

        for name in self.targetFieldNames:
            value = self.form[name].value
            setattr(target, name, value)
                
        for name in options:
            setattr(target, name, options[name])
        if auto_commit:
            session.commit()
        return target

    def deleteTarget(self, auto_commit=True):
        session, target = self.getTargetWithSession()
        if target == None:
            return
        
        session.delete(target)
        if auto_commit:
            session.commit()

    def isPostBack(self):
        return self.getParam("_POST_BACK") == "true"

    def _validateHiddenToken(self):
        #CSRF防止用トークンの検証、別メソッドにするのはテストフレームワーク側でオーバーライドするため
        return not(self.session.sessionid != None and self.getParam("_rita_hidden_token") != self.session["_rita_hidden_token"])
    
    def getFormState(self):
        #memo:結果をキャッシュした方がいいかも
        action = self.getParam("_ACTION")
        cancel_clicked = self.getParam("_CANCEL") != None
        if self.getParam("__mode__") == "delete":
            if cancel_clicked:
                return FormState.CANCELED
            if self.isPostBack() and self._validateHiddenToken() and action == "complete":
                return FormState.DELETE_READY
            else:
                return FormState.DELETE_CONFIRM
        else:
            if self.isPostBack() and self._validateHiddenToken() and self._validateForm():
                if self.showInputConfirm == False or action == "complete":
                    if cancel_clicked:
                        return FormState.INPUTTING
                    else:
                        return FormState.INPUT_READY
                else:
                    if cancel_clicked:
                        return FormState.CANCELED
                    else:
                        return FormState.INPUT_CONFIRM
        return FormState.INPUTTING

    def renderFormBegin(self):
        return """<form method="POST">"""
    
    def renderFormEnd(self):
        ret = ["""<input type="hidden" name="_POST_BACK" value="true"/>"""]
        if self.session.sessionid != None:
            ret.append("""<input type="hidden" name="_rita_hidden_token" value="%s"/>""" % (self.session["_rita_hidden_token"]))

        if self.getFormState() == FormState.DELETE_CONFIRM or (self.showInputConfirm == False or self.getFormState() == FormState.INPUT_CONFIRM):
            ret.append("""<input type="hidden" name="_ACTION" value="complete"/>""")
                            
        ret.append("</form>")
        return "\n".join(ret)
    
    def renderLabel(self, name):
        return self.fields[name].name

    def renderInput(self, name):
        return self.fields[name].render(name, self.form[name].value, readonly=self.getFormState() in [FormState.DELETE_CONFIRM, FormState.INPUT_CONFIRM])

    def renderError(self, name):
        return "<br/>".join(self.form[name].errors)
    
    def renderSubmit(self):
        if self.getFormState() == FormState.DELETE_CONFIRM:
            return """<input type="submit" value="削除">"""
        elif self.showInputConfirm == False or self.getFormState() == FormState.INPUT_CONFIRM:
            return """<input type="submit" value="送信">"""
        else:
            return """<input type="submit" value="入力内容の確認">"""

    def renderCancel(self):
        value = self.attr["_"]("キャンセル")
        if self.getFormState() == FormState.INPUT_CONFIRM:
            value = self.attr["_"]("入力画面に戻る")
        return """<input type="submit" name="_CANCEL" value="%s">""" % (value)
