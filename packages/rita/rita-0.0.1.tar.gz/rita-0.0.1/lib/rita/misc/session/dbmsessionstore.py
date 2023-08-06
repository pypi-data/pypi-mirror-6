# -*- coding: utf-8 -*-
from datetime import datetime
import time
import json

from rita.session import ISessionStore

class DbmSessionStore(ISessionStore):
    def __init__(self, dbm):
        self.db = dbm

    def exists(self, sessionid):
        if not sessionid:return False
        try:
            return self.db[sessionid] != None
        except KeyError:
            return False
    
    def get(self, sessionid, key):
        if not self.exists(sessionid):
            #そもそもセッションが存在しない
            return None
        else:
            dic = json.loads(str(self.db[sessionid].decode("utf8")))
            self.set(sessionid, "lastAccessed", datetime.now())
            if not key in dic:
                #セッションはあるがセッション変数が存在しない
                return None
            else:
                return dic[key]

    def set(self, sessionid, key, value, create=False):
        if not self.exists(sessionid):
            #そもそもセッションが存在しない
            if not create:
                raise KeyError("sessionid not found:" + sessionid)
            self.db[sessionid] = json.dumps({"lastAccessed":self._totimestamp(datetime.now())})
            
        dic = json.loads(str(self.db[sessionid].decode("utf8")))
        dic[key] = value
        dic["lastAccessed"] = self._totimestamp(datetime.now())
        for k in dic:
            dic[k] = str(dic[k])
        self.db[sessionid] = json.dumps(dic)
    
    def _totimestamp(self, dt):
        return str(time.mktime(dt.timetuple()))
    
    def delete(self, sessionid, key=None):
        if key:
            del self.db[sessionid][key]
        else:
            del self.db[sessionid]
        
    def close(self):
        if hasattr(self.db, "close"):
            self.db.close()
