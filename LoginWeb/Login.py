import flask_login
from ContainerServer import *

login_manager = flask_login.LoginManager()

users = {'linnil1': {'password': 'test'}}

class LoginUser(flask_login.UserMixin):
    def __init__(self, name):
        self.id = name
        self.user = User(name)

@login_manager.user_loader
def user_loader(name):
    if name not in users:
        return None

    return LoginUser(name)


def requestParse(request):
    name = request.form.get('userName')
    user = user_loader(name)
    if not user:
        return None
    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    is_authenticated = request.form['userPassword'] == users[name]['password']

    if not is_authenticated:
        return None

    flask_login.login_user(user)
    return user
