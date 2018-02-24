from .start import set_db, query_db
import time
from requests_unixsocket import post

class UserError:
    pass

class User:
    def __init__(self, name):
        self.name = name
        self.netName = "labserver_mynet"
        self.sock= "http+unix://%2Fapp%2Fsock%2FDockerServer.sock"

    def getToken(self, queryStr, queryObj, one=True):
        qdata = query_db(queryStr, queryObj, one=one)
        return qdata

    def checkID(self, containerID):
        ddata = self.getToken("SELECT * FROM tokens WHERE name = ? AND boxid = ?",
                              (self.name, containerID))
        if not ddata:
            raise UserError
        return ddata

    def lists(self):
        print("list", self.name)
        ddata = self.getToken("SELECT * FROM tokens WHERE name = ?", (self.name,), one=False)
        return [{"id"  : d['boxid'],
                 "name": d['boxname'],
                 "time": d['time'] } for d in ddata]

    def resume(self, containerID):
        ddata = checkID(containerID)
        mytoken = ddata["tokenname"]

        rep = post(self.sock + "/start", data={'id': containerID}).json()
        if rep.get('error'):
            raise UserError

        cont = post(self.sock + "/search", data={'key': containerID}).json()
        if cont.get('error'):
            raise UserError
        if not cont['ip']:
            raise UserError

        set_db("UPDATE tokens SET time = ?, tokenip = ? WHERE boxid = ?",
               (str(time.time()),
                cont['ip'],
                containerID))
        # my_vnc code should add 5900 by itself
        print("resume", dict(ddata))
        return mytoken

    # def reset(self, containerID):
    #     print("reset", containerID)
    #     return True

    def stop(self, containerID):
        checkID(containerID)
        rep = post(self.sock + "/stop", data={'id': containerID}).json()
        if rep.get('error'):
            raise UserError
        print("stop", containerID)
        return True

    def restart(self, containerID):
        checkID(containerID)
        rep = post(self.sock + "/restart", data={'id': containerID}).json()
        if rep.get('error'):
            raise UserError
        print("restart", containerID)
        return True

    def add(self):
        """ INSERT INTO tokens (tokenname, tokenip, name, boxid, boxname, time) VALUES (?,?,?,?,?,?) """
        packed = [self.name + "_0", "172.25.0.5:5900", self.name, "id", "name_id", str(time.time())]
        set_db("INSERT INTO tokens (tokenname, tokenip, name, boxid, boxname, time) VALUES (?,?,?,?,?,?)", packed)
        print("add", packed)
        return packed[0]
