import flask
import flask_login
import flask_bcrypt
from getpass import getpass
from .ContainerServer import *
from .start import query_db, get_db

login_manager = flask_login.LoginManager()
bcrypt = flask_bcrypt.Bcrypt()

class LoginUser(flask_login.UserMixin):
    def __init__(self, u):
        self.id = u[0]
        self.password = u[1]
        self.user = User(self.id)
    def checkPassword(self, password):
        return bcrypt.check_password_hash(self.password, password)

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
    with app.app_context():
        cur = get_db()
        cur.execute("INSERT INTO login (name, pass) VALUES (?, ?)", (name, password))
        cur.commit()
        cur.close()
