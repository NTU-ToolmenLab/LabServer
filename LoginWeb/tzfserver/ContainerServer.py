from .start import set_db, query_db
import time
class UserError:
    pass

import time
class User:
    def __init__(self, name):
        self.name = name

    def getToken(self, queryStr, queryObj):
        qdata = query_db(queryStr, queryObj, one=True)
        return qdata

    def lists(self):
        print("list")
        ddata = self.getToken("SELECT * FROM tokens WHERE name = ?", (self.name,))
        return [{"id"  : ddata['boxid'],
                 "name": ddata['boxname'],
                 "time": ddata['time'] }]

    def reset(self, containerID):
        print("reset", containerID)
        return packed[0]
        return True

    def resume(self, containerID):
        ddata = self.getToken("SELECT * FROM tokens WHERE name = ? AND boxid = ?",
                              (self.name, containerID))
        set_db("UPDATE tokens SET time = ? WHERE boxid = ?", (str(time.time()), containerID))
        mytoken = ddata["tokenname"]
        print("resume", ddata)
        return mytoken

    def remove(self, containerID):
        print("remove", containerID)
        return True

    def restart(self, containerID):
        print("restart", containerID)
        return True

    def add(self):
        """ INSERT INTO tokens (tokenname, tokenip, name, boxid, boxname, time) VALUES (?,?,?,?,?,?) """
        packed = [self.name + "_0", "172.25.0.5:5900", self.name, "id", "name_id", str(time.time())]
        set_db("INSERT INTO tokens (tokenname, tokenip, name, boxid, boxname, time) VALUES (?,?,?,?,?,?)", packed)
        print("add", packed)
        return packed[0]
