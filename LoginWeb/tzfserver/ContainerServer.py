from .start import set_db, query_db
import time
import docker
class UserError:
    pass

class User:
    def __init__(self, name):
        self.name = name
        self.con = docker.from_env().containers
        self.netName = "labserver_mynet"

    def getToken(self, queryStr, queryObj, one=True):
        qdata = query_db(queryStr, queryObj, one=one)
        return qdata

    def lists(self):
        print("list", self.name)
        ddata = self.getToken("SELECT * FROM tokens WHERE name = ?", (self.name,), one=False)
        return [{"id"  : d['boxid'],
                 "name": d['boxname'],
                 "time": d['time'] } for d in ddata]

    def reset(self, containerID):
        print("reset", containerID)
        return True

    def resume(self, containerID):
        ddata = self.getToken("SELECT * FROM tokens WHERE name = ? AND boxid = ?",
                              (self.name, containerID))
        if not ddata:
            raise UserError
        mytoken = ddata["tokenname"]

        container = self.con.get(containerID)
        set_db("UPDATE tokens SET time = ?, tokenip = ? WHERE boxid = ?",
               (str(time.time()),
                container.attrs['NetworkSettings']['Networks'][self.netName]['IPAddress'],
                containerID))
        # my_vnc code should add 5900 by itself
        print("resume", dict(ddata))
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
