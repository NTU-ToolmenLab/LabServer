import time
from flask_sqlalchemy import SQLAlchemy
import flask_login
import passlib.hash

db = SQLAlchemy()
login_manager = flask_login.LoginManager()

class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(300), nullable=True)
    admin = db.Column(db.Boolean(32), nullable=True)

    def __str__(self):
        return self.name

    def checkPassword(self, password):
        return passlib.hash.sha512_crypt.verify(password, self.password)

@login_manager.user_loader
def user_loader(id):
    return User.query.get(id)

def getUserId(name, password):
    u = User.query.all()
    print(u)
    u = User.query.filter_by(name=name).first()
    if not u:
        return None
    if not u.checkPassword(password):
        return None
    return user_loader(u.id)
