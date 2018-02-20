from .start import query_db, get_db
import time
class UserError:
    pass

import time
class User:
    def __init__(self, name):
        self.name = name

    def getToken(self, queryStr, queryObj):
        qdata = query_db(queryStr, queryObj, one=True)
        if not qdata:
            raise UserError
        kdata = ["tokenname", "tokenip", "name", "boxid", "boxname", "time"]
        return dict(zip(kdata, qdata))

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
        ddata = self.getToken("SELECT * FROM tokens WHERE name = ? AND boxid = ?", (self.name, containerID))
        print("resume", ddata)
        return ddata["tokenname"]

    def remove(self, containerID):
        print("remove", containerID)
        return True

    def restart(self, containerID):
        print("restart", containerID)
        return True

    def add(self):
        """ INSERT INTO tokens (tokenname, tokenip, name, boxid, boxname, time) VALUES (?,?,?,?,?,?) """
        packed = [self.name + "_0", "172.25.0.5:5900", self.name, "id", "name_id", str(time.time())]
        with app.app_context():
            cur = get_db()
            cur.execute("INSERT INTO tokens (tokenname, tokenip, name, boxid, boxname, time) VALUES (?,?,?,?,?,?)", packed)
            cur.commit()
            cur.close()
        print("add", packed)
        return packed[0]
