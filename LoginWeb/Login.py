import flask
import flask_login
import flask_bcrypt
from ContainerServer import *
from start import query_db

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
    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    is_authenticated = user.checkPassword(request.form['userPassword'])

    if not is_authenticated:
        return None

    flask_login.login_user(user)
    return user

# users = {'linnil1': {'password': bcrypt.generate_password_hash('test')}}
# print(users)
