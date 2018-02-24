from .start import set_db, query_db
import time
from requests_unixsocket import post

class UserError:
    pass

"""
# database
CREATE TABLE tokens (
  tokenname   TEXT PRIMARY KEY,
  user        TEXT NOT NULL,
  tokenip     TEXT,
  tokenstatus TEXT,
  boxid       TEXT,
  boxname     TEXT NOT NULL,
  boxstatus   TEXT
);
"""

class User:
    def __init__(self, name):
        self.name = name
        self.netName = "labserver_mynet"
        self.sock= "http+unix://%2Fapp%2Fsock%2FDockerServer.sock"

    def getToken(self, queryStr, queryObj, one=True):
        qdata = query_db(queryStr, queryObj, one=one)
        return qdata

    def checkID(self, containerID):
        ddata = self.getToken("SELECT * FROM tokens WHERE user = ? AND boxid = ?",
                              (self.name, containerID))
        if not ddata:
            raise UserError
        return ddata

    def lists(self):
        print("list", self.name)
        ddata = self.getToken("SELECT * FROM tokens WHERE user = ?", (self.name,), one=False)

        list_box = []
        for d in ddata:
            cont = post(self.sock + "/search", data={'key': d['boxname']}).json()
            if cont.get('error'):
                raise UserError
            set_db("UPDATE tokens SET boxid = ?, boxstatus = ? WHERE boxname = ?",
                   (cont['id'], cont['status'], d['boxname']))
            list_box.append({"id"  :   cont['id'],
                             "name":   cont['name'],
                             "status": cont['status']})
        return list_box

    def resume(self, containerID):
        ddata = self.checkID(containerID)
        mytoken = ddata["tokenname"]

        rep = post(self.sock + "/start", data={'id': containerID}).json()
        if rep.get('error'):
            raise UserError

        cont = post(self.sock + "/search", data={'key': containerID}).json()
        if cont.get('error'):
            raise UserError
        if not cont['ip']:
            raise UserError

        set_db("UPDATE tokens SET tokenstatus = ?, boxstatus = ?, tokenip = ? WHERE boxid = ?",
               ("init", cont['status'],
                cont['ip'], containerID))
        # my_vnc code should add 5900 by itself
        print("resume", dict(ddata))
        return mytoken

    # def reset(self, containerID):
    #     print("reset", containerID)
    #     return True

    def stop(self, containerID):
        self.checkID(containerID)
        rep = post(self.sock + "/stop", data={'id': containerID}).json()
        if rep.get('error'):
            raise UserError
        print("stop", containerID)
        return True

    def restart(self, containerID):
        self.checkID(containerID)
        rep = post(self.sock + "/restart", data={'id': containerID}).json()
        if rep.get('error'):
            raise UserError
        print("restart", containerID)
        return True

    def add(self):
        tokname = self.name
        packed = [tokname, self.name, "labserver_" + tokname + "_1"] # docker compose naming
        set_db("INSERT INTO tokens (tokenname, user, boxname) VALUES (?,?,?)", packed)
        print("add", packed)
        return packed[0]
