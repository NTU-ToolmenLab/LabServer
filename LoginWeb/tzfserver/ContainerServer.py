from .start import set_db, query_db
import time
from requests_unixsocket import post
import passlib.hash
import time

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
    def __init__(self, name, admin=0):
        self.name = name
        self.netName = "labserver_mynet"
        self.sock= "http+unix://%2Fapp%2Fsock%2FDockerServer.sock"
        self.isadmin = int(admin)

    def getToken(self, queryStr, queryObj=(), one=True):
        qdata = query_db(queryStr, queryObj, one=one)
        return qdata

    def checkID(self, containerID):
        if self.isadmin:
            ddata = self.getToken("SELECT * FROM tokens WHERE boxid = ?", (containerID,))
        else:
            ddata = self.getToken("SELECT * FROM tokens WHERE user = ? AND boxid = ?",
                                  (self.name, containerID))
        if not ddata:
            raise UserError
        return ddata

    def checkVNCtoken(self, token):
        if self.isadmin:
            ddata = query_db("SELECT * FROM tokens WHERE tokenname = ?", (token,), one=True)
        else:
            ddata = query_db("SELECT * FROM tokens WHERE tokenname = ? AND user = ?", (token, self.name), one=True)
        if not ddata:
            return ""
            raise UserError
        return qdata['tokenstatus'] + '|passowrd'

    def lists(self):
        print("list", self.name)
        if self.isadmin:
            ddata = self.getToken("SELECT * FROM tokens", one=False)
        else:
            ddata = self.getToken("SELECT * FROM tokens WHERE user = ?", (self.name,), one=False)

        list_box = []
        for d in ddata:
            cont = post(self.sock + "/search", data={'key': d['boxname']}).json()
            if cont.get('error'):
                print("Error", d['boxname'])
                continue
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
               ("init" + passlib.hash.hex_md5.encrypt(str(time.time())), cont['status'],
                cont['ip'], containerID))

        if not self.isadmin:
            pw = self.getToken("SELECT * FROM login where name = ?", (self.name,), one=True)['pass']
            self.passwdone(pw, containerID)

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

    def passwd(self, pw):
        ddata = self.getToken("SELECT * FROM tokens WHERE user = ?", (self.name,), one=False)
        for i in ddata:
            self.passwdone(pw, i['boxname'])
        print("passwd ", self.name)
        return True

    def passwdone(self, pw, containerID):
        rep = post(self.sock + "/passwd", data={'id': containerID,
                                                'pw': pw}).json()
        if rep.get('error'):
            raise UserError
        print("passwd ", containerID)

def add_token(name, tokenname, realtoken=""):
    # in this case realtoken = "labserver_" + tokenname + "_1"
    if not realtoken:
        realtoken = tokenname
    assert(not query_db('SELECT tokenname FROM tokens WHERE tokenname = ?',
                        [tokenname], one=True))
    # docker compose naming
    set_db("INSERT INTO tokens (tokenname, user, boxname) VALUES (?,?,?)",
           (tokenname, name, realtoken))

def std_add_token(user):
    print("tokenname ")
    tokenname = input()
    print("realtoken ")
    realtoken = input()
    add_token(user, tokenname, realtoken)
