# -*- coding: utf-8 -*-
from datetime import datetime
import json

from rita.session import ISessionStore

class PyhsSessionStore(ISessionStore, object):
    """
    from pyhs import Manager
    pyhs_config = {
            "read_servers":[("inet", "localhost", 9998)],
            "write_servers":[("inet", "localhost", 9999)],
            "debug":False}
    hs = Manager(**pyhs_config)
    store = PyhsSessionStore(hs,"db","table")
    """
    def __init__(self, manager, db_name, table_name):
        self.manager = manager
        self.db_name = db_name
        self.table_name = table_name
    
    def _getDataDict(self, sessionid):
        """セッションのdata列をdictとして取得"""
        result = self.manager.get(self.db_name, self.table_name, ["sessionid", "last_accessed", "data"], sessionid)
        if len(result) == 0:
            return None
        
        dic = dict(result)
        return json.loads(dic["data"])
    
    def exists(self, sessionid):
        if not sessionid:return False
        result = self.manager.get(self.db_name, self.table_name, ["sessionid"], sessionid)
        return len(result) == 1
    
    def get(self, sessionid, key):
        result = self.manager.get(self.db_name, self.table_name, ["sessionid", "orgid", "last_accessed", "data"], sessionid)
        if len(result) == 0:
            #セッションがない
            return None
        else:
            #フィールドにアクセスがあったので最終アクセス日を更新
            self.manager.update(self.db_name, self.table_name, "=", ["last_accessed"], [sessionid], [str(datetime.now())])

            #組織IDと最終アクセス日はテーブル自体のフィールド、それ以外はdata列に入ったjsonを見る
            dic = dict(result)
            if key == "orgid":
                return int(dic["orgid"])
            elif key == "last_accessed": 
                return None
            else:
                datadic = json.loads(dic["data"])
                if not key in datadic:
                    #セッションはあるがセッション変数が存在しない
                    return None
                else:
                    return datadic[key]
    
    def set(self, sessionid, key, value, create=False):
        dic = self._getDataDict(sessionid)
        if dic == None:
            #そもそもセッションが存在しない
            if not create:
                raise KeyError("sessionid not found:" + sessionid)
            else:
                val = [("sessionid", sessionid), ("data", json.dumps({key:value}))]
                tmp = self.manager.insert(self.db_name, self.table_name, val) #Datetimeはどう挿入するか
                dic = dict(val)
                return

        #組織IDと最終アクセス日はテーブル自体のフィールド、それ以外はdata列に入ったjsonを見る
        fields, values = ["last_accessed"], [str(datetime.now())]
        if key == "orgid":
            fields.append("orgid")
            values.append(str(value))
        elif key == "last_accessed":
            #最終更新日は直接更新させない
            pass
        else:
            dic[key] = value
            fields.append("data")
            values.append(json.dumps(dic))
        self.manager.update(self.db_name, self.table_name, '=', fields, [sessionid], values)
    
    #def _totimestamp(self, dt):
    #    return str(time.mktime(dt.timetuple()))
    
    def delete(self, sessionid, key=None):
        """keyを指定した場合はそのフィールドのみ、指定しなければセッションのレコードそのものを削除する"""
        if key:
            dic = self._getDataDict(sessionid)
            if key in dic:
                del dic[key]
                self.manager.update(self.db_name, self.table_name, '=', ['data'], [sessionid], [json.dumps(dic)])
        else:
            self.manager.delete(self.db_name, self.table_name, '=', ['sessionid'], [sessionid])
        
    def close(self):
        self.manager.purge()
