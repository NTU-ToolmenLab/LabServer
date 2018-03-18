import flask
import flask_login
import time
import passlib.hash
from getpass import getpass
from .ContainerServer import *
from .start import set_db, get_db

login_manager = flask_login.LoginManager()

class LoginUser(flask_login.UserMixin):
    def __init__(self, u):
        self.id = u['name']
        self.password = u['pass']
        self.time = u['time']
        self.user = User(self.id)
    def checkPassword(self, password):
        return passlib.hash.sha512_crypt.verify(password, self.password)

    def setPassword(self, password):
        self.password = passlib.hash.sha512_crypt.encrypt(password)
        set_db('UPDATE login SET pass = ?, time = ? WHERE name = ?',
               (self.password, time.time(), self.id))

@login_manager.user_loader
def user_loader(name):
    u = query_db('SELECT * FROM login WHERE name = ?', [name], one=True)
    if not u:
        return None
    return LoginUser(u)

def requestParse(request):
    user = user_loader(request.form.get('userName'))
    if not user:
        return None

    is_authenticated = user.checkPassword(request.form['userPassword'])
    if not is_authenticated:
        return None

    flask_login.login_user(user)
    return user

def setPW(user, oldone, newone):
    if not user.checkPassword(oldone):
        return "Wrong password"
    if len(newone) < 8:
       return "Password should be more than 8 characters"
    user.setPassword(newone)
    return "ok"

def std_add_user():
    print("Username ")
    name = input()
    passwd = getpass()
    passwd1 = getpass("Password Again: ")
    assert(passwd == passwd1 and len(passwd) >= 8)
    return add_user(name, passwd)

def add_user(name, passwd='test'): # change it
    assert(not query_db('SELECT name FROM login WHERE name = ?', [name], one=True))
    password = passlib.hash.sha512_crypt.encrypt(passwd)
    set_db("INSERT INTO login (name, pass, time) VALUES (?, ?, ?)", (name, password, 0))
    return name
