class UserError:
    pass

import time
class User:
    def __init__(self, name):
        self.name = name

    def list(self):
        print("list")
        return [{"id":"id0", "name": self.name + "_" + "name0", "time": time.strftime("%c"), "url":"http://google.com"},
                {"id":"id1", "name": self.name + "_" + "name1", "time": time.strftime("%c"), "url":"http://github.com"}]

    def reset(self, containerID):
        print("reset", containerID)
        return True

    def resume(self, containerID):
        print("resume", containerID)
        return True

    def remove(self, containerID):
        print("remove", containerID)
        return True

    def restart(self, containerID):
        print("restart", containerID)
        return True

    def add(self):
        add_id = "ID"
        print("add", add_id)
        return add_id

