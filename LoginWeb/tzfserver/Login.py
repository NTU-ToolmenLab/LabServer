import flask
import flask_login
import flask_bcrypt
from getpass import getpass
from .ContainerServer import *
from .start import set_db, get_db

login_manager = flask_login.LoginManager()
bcrypt = flask_bcrypt.Bcrypt()

class LoginUser(flask_login.UserMixin):
    def __init__(self, u):
        self.id = u['name']
        self.password = u['pass']
        self.user = User(self.id)
    def checkPassword(self, password):
        return bcrypt.check_password_hash(self.password, password)
    def setPassword(self, password):
        set_db('UPDATE login SET pass = ? WHERE name = ?',
               (bcrypt.generate_password_hash(password), self.id))

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
    # if len(newone) < 8:
    #    return "Password should be more than 8 characters"
    user.setPassword(newone)
    return "ok"

# users = {'linnil1': {'password': bcrypt.generate_password_hash('test')}}
# print(users)

def add_user(app):
    """ usage: import start; start.add_user(start.app); """
    # input
    print("Username ")
    name = input()
    assert(not query_db('SELECT * FROM login WHERE name = ?', [name], one=True))
    passwd = getpass()
    passwd1 = getpass("Password Again: ")
    assert(passwd == passwd1 and len(passwd) < 6)
    password = bcrypt.generate_password_hash(passwd)

    # insert it
    set_db("INSERT INTO login (name, pass) VALUES (?, ?)", (name, password))
