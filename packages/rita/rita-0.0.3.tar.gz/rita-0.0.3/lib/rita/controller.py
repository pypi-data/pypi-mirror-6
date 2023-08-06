# -*- coding: utf-8 -*-
import sys
import cgi
import gettext
import unicodedata
import json
from io import BytesIO
from collections import OrderedDict

try:
    #makoがなくても動作するようにする
    from mako.lookup import TemplateLookup
except ImportError:
    pass

try:
    #sqlalchemyがなくても動作するようにする
    from sqlalchemy import Integer
    from rita.validator import Validator
except ImportError:
    pass
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
    """後に続く処理をせずにレスポンスを出力するときに投げる例外"""
    pass

class BaseController(object):
    def __init__(self):
        self.env = {}
        self.attr = {"page":self}
        self.charset = self.get_charset()
        self.outputExpiredHeader = True

        self._headers = {}
        self._status = 200
        self._params = None
        self._fieldstorage = None
        self._output_buffer = BytesIO()

    def application(self, env, start_response):
        """WSGIアプリケーションの本体。基本的にはオーバーライドはしない前提"""
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
    
    #begin:各アプリケーション側でオーバーライドするメソッド
    def initialize(self):
        """初期化や前処理を行う"""
        pass #
    
    def auth(self):
        """認証と認可を行う"""
        pass

    def process(self):
        """メインの処理"""
        pass
    #end:各アプリケーション側でオーバーライドするメソッド

    #begin:必要に応じて継承先でオーバーライドするメソッド
    def get_current_user(self):
        return None

    def get_charset(self):
        return "utf8"    

    def get_locale_dir(self):
        pass

    def get_languages(self):
        return ["ja-jp"]

    def get_http_session(self):
        return HttpSession(self)

    def get_http_session_store(self):
        return {}

    def finalize(self):
        """終了処理。デフォルトではセッションストアから切断する"""
        try:
            self.session.close()
        except:pass
    
    def get_document_root(self):
        return "."
    #end:必要に応じて継承先でオーバーライドするメソッド

    #begin:アプリケーションの実装において呼び出す想定のメソッド（オーバーライドはされない想定）
    def output(self, s):
        """出力バッファに文字列を直接出力する"""
        self._output_buffer.write(s.encode(self.charset))

    def status(self, code):
        """ステータスコードを設定する"""
        self._status = code
        
    def header(self, name, value=None):
        """ヘッダーを出力する"""
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

    def finish_response(self):
        """リクエストの処理を終了する（残りの処理はしない）"""
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

    def render_string(self, file_name=None):
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
            mylookup = TemplateLookup(directories=[self.get_document_root() + folder], input_encoding="utf-8", default_filters=["h", "str"])
        else:
            default_filters = ["decode." + self.charset] + ["h"]
            mylookup = TemplateLookup(directories=[self.get_document_root() + folder], input_encoding="utf-8", default_filters=default_filters)
        mytemplate = mylookup.get_template(file_name)

        return mytemplate.render_unicode(**self.attr)

    def render(self, file_name=None):
        """テンプレートから文字列を生成して出力バッファに出力する"""
        self.output(self.render_string(file_name))
        
    def get_param(self, name, default=None):
        """パラメータを取得する"""
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

    def redirect(self, location, finish_response=True, permit_external_site=False):
        """リダイレクトヘッダを出力する,finish_response=Trueならそれ以降の処理はしない"""
        self.status(302)
        self.header("Location", location)
        if not permit_external_site:
            if len(location) > 2: #/から始まるURL以外のサイトにリダイレクトさせない
                #FIXME route.pyなどからのホワイトリスト対応の方がいいかも
                if not(location.startswith("/") and location[1] != "/"):
                    raise ValueError("redirect to external site is not permitted.")
        
        if finish_response:
            self.finish_response()
    #end:アプリケーションの実装において呼び出す想定のメソッド（オーバーライドはされない想定）
    
    #begin:private
    def _initialize(self):
        self._params = self.FieldStorage()
        self.session = self.get_http_session()
        self.currentUser = self.get_current_user()
        locale_dir = self.get_locale_dir()
        if locale_dir != None:
            if sys.version_info.major >= 3:
                self.attr["_"] = gettext.Catalog("messages", locale_dir, self.get_languages(), fallback=True).gettext
            else:
                self.attr["_"] = self._py2_i18n_helper
        else:
            self.attr["_"] = lambda x:x

    def _py2_i18n_helper(self, s):
        #python2系だとバイト型の文字列が渡される場合があるため
        if not isinstance(s, unicode):
            s = s.decode("utf8")  
        return gettext.Catalog("messages", self.get_locale_dir(), self.get_languages(), fallback=True).gettext(s)

    def _preprocess(self):
        pass #親クラスでは何もしない（フレームワーク内の継承先で必要に応じて実装する）
    #end:private

class _FormInput(object):
    def __init__(self, value):
        self.value = value
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

    #begin:各アプリケーション側でオーバーライドするメソッド
    def validateForm(self):
        return True
    #end:各アプリケーション側でオーバーライドするメソッド

    #begin:必要に応じて継承先でオーバーライドするメソッド
    def get_db_session(self):
        """sqlalchemyのセッションを返す"""
        return None

    def get_primary_key(self):
        """フォーム編集や削除時の主キーを取得する"""
        splited = str(self.env["PATH_INFO"]).split("/")
        try:
            return int(splited[-1])
        except:
            return None

    def prepare_form(self):
        """DBからフォームの初期値を用意する"""
        target = self.get_target()
        if target != None:
            for field_name in self.targetFieldNames:
                self.form[field_name].value = getattr(target, field_name) 
    #end:必要に応じて継承先でオーバーライドするメソッド
    
    #begin:アプリケーションの実装において呼び出す想定のメソッド（オーバーライドはされない想定）
    def is_post_back(self):
        return self.get_param("_POST_BACK") == "true"

    def get_form_state(self):
        #memo:結果をキャッシュした方がいいかも
        action = self.get_param("_ACTION")
        cancel_clicked = self.get_param("_CANCEL") != None
        if self.get_param("__mode__") == "delete":
            if cancel_clicked:
                return FormState.CANCELED
            if self.is_post_back() and self._validate_hidden_token() and action == "complete":
                return FormState.DELETE_READY
            else:
                return FormState.DELETE_CONFIRM
        else:
            if self.is_post_back() and self._validate_hidden_token() and self._validate_form():
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

    def get_param(self, name, default=None):
        #数値のフィールドの場合は全角数値は自動的に半角に変換する
        ret = BaseController.get_param(self, name, default)
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

    def get_target(self, use_cache=True):
        """編集や削除対象のモデルを取得する（新規作成の場合はNoneを返す）"""
        if use_cache and self._cached_target != None:
            return self._cached_target
        session, ret = self.get_target_with_session()
        self._cached_target = ret
        return ret

    def get_target_with_session(self):
        """編集や削除対象のモデルを、関連したDBのセッションと共に取得する"""
        session = self.get_db_session()
        if self.targetClass != None:
            if self.get_primary_key() != None:
                return session, session.query(self.targetClass).filter(self.targetClass.id == int(self.get_primary_key()))[0]
        return session, None
            
    def update_target(self, options=None, auto_commit=True):
        """フォーム内容に基づいてモデルを更新する"""
        if options == None:options = {} 
        session, target = self.get_target_with_session()
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

    def delete_target(self, auto_commit=True):
        """モデルを削除する"""
        session, target = self.get_target_with_session()
        if target == None:
            return
        
        session.delete(target)
        if auto_commit:
            session.commit()
    #end:アプリケーションの実装において呼び出す想定のメソッド（オーバーライドはされない想定）

    #begin:フォーム描画用メソッド
    def render_form_begin(self):
        return """<form method="POST">"""
    
    def render_form_end(self):
        ret = ["""<input type="hidden" name="_POST_BACK" value="true"/>"""]
        if self.session.sessionid != None:
            ret.append("""<input type="hidden" name="_rita_hidden_token" value="%s"/>""" % (self.session["_rita_hidden_token"]))

        if self.get_form_state() == FormState.DELETE_CONFIRM or (self.showInputConfirm == False or self.get_form_state() == FormState.INPUT_CONFIRM):
            ret.append("""<input type="hidden" name="_ACTION" value="complete"/>""")
                            
        ret.append("</form>")
        return "\n".join(ret)
    
    def render_label(self, name):
        return self.fields[name].name

    def render_input(self, name):
        return self.fields[name].render(name, self.form[name].value, readonly=self.get_form_state() in [FormState.DELETE_CONFIRM, FormState.INPUT_CONFIRM])

    def render_error(self, name):
        return "<br/>".join(self.form[name].errors)
    
    def render_submit(self):
        if self.get_form_state() == FormState.DELETE_CONFIRM:
            return """<input type="submit" value="削除">"""
        elif self.showInputConfirm == False or self.get_form_state() == FormState.INPUT_CONFIRM:
            return """<input type="submit" value="送信">"""
        else:
            return """<input type="submit" value="入力内容の確認">"""

    def render_cancel(self):
        value = self.attr["_"]("キャンセル")
        if self.get_form_state() == FormState.INPUT_CONFIRM:
            value = self.attr["_"]("入力画面に戻る")
        return """<input type="submit" name="_CANCEL" value="%s">""" % (value)
    #end:フォーム描画用メソッド

    #begin:private
    def _preprocess(self):
        self.form = {}
        for name in self.fields.keys():
            self.form[name] = _FormInput(self.get_param(name, ""))
        if not self.is_post_back():
            self.prepare_form()

    def _validate_form(self):
        #一度呼び出し済みなら結果のみを返す
        if self._validation_result != None:
            return self._validation_result

        if not self.is_post_back():return
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

    def _validate_hidden_token(self):
        #CSRF防止用トークンの検証、別メソッドにするのはテストフレームワーク側でオーバーライドするため
        return not(self.session.sessionid != None and self.get_param("_rita_hidden_token") != self.session["_rita_hidden_token"])
    #end:private
