import flask_login

login_manager = flask_login.LoginManager()

users = {'test': {'password': 'test'}}

class User(flask_login.UserMixin):
    def __init__(self, name):
        self.id = name

@login_manager.user_loader
def user_loader(name):
    if name not in users:
        return None

    return User(name)


def requestParse(request):
    print(request.form)
    name = request.form.get('userName')
    print(name)
    user = user_loader(name)
    if not user:
        return
    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    is_authenticated = request.form['userPassword'] == users[name]['password']
    return user, is_authenticated

