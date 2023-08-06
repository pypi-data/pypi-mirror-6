# -*- coding: utf-8 -*-
import sys
from io import BytesIO, StringIO

class Facade(object):
    def build_application(self, routes):
        """WSGIアプリケーションを生成する"""
        def app(env, start_response):
            try:
                klass = self.get_handler_class(env, routes)
                if klass != None:
                    #処理するクラスが見つかった
                    return klass().application(env, start_response)
                else:
                    #処理するクラスが見つからなかった
                    return self.handle404(env, start_response)
            except Exception as exception:
                #未処理の例外が発生（500エラー）
                return self.handle500(exception, start_response)
        return app

    #begin:必要に応じてオーバーライド
    def get_handler_class(self, env, routes):
        """リクエストされたURLから、担当クラスを返す"""
        for route in routes:
            if env["PATH_INFO"] == route[0] or (route[0] != "/" and env["PATH_INFO"].startswith(route[0])):
                url, full_path = route
                if type(full_path) == str:
                    splited_path = full_path.split('.')
                    module_path, klass = '.'.join(splited_path[:-1]), splited_path[-1]
                    module = __import__(module_path, globals(), locals(), [""])
                    return getattr(module, klass)
                else:
                    return full_path

    def handle404(self, env, start_response):
        status = '404 Not Found'
        response_headers = [('Content-Type', 'text/html;charset=utf-8')]
        start_response(status, response_headers)
        return ["404 Not Found. " + env["PATH_INFO"] + " "*512]
        
    def handle500(self, exception, start_response):
        status = '500 Internal Server Error'
        import traceback
        if sys.version_info.major >= 3:
            buf = StringIO()
            traceback.print_exc(30, buf)
        else:
            buf = BytesIO()
            traceback.print_exc(exception, buf)
        detail = buf.getvalue()
        buf.close()
        response_headers = [('Content-Type', 'text/html')]
        sys.stderr.write(detail)
        start_response(status, response_headers)
        return [detail.replace("\n", "<br/>").replace(" ", "&nbsp;"*2)]
    #end:必要に応じてオーバーライド
