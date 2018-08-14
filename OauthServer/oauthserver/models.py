import time
from flask_sqlalchemy import SQLAlchemy
import flask_login
import passlib.hash
import time
import logging

logger = logging.getLogger('oauthserver')
db = SQLAlchemy()
login_manager = flask_login.LoginManager()

class User(db.Model, flask_login.UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(300), nullable=False)
    passtime = db.Column(db.Float, default=0)
    admin = db.Column(db.Boolean(32), default=0, nullable=False)

    def __str__(self):
        return '<User {}>'.format(self.name)

    def checkPassword(self, password):
        return passlib.hash.sha512_crypt.verify(password, self.password)
    def setPassword(self, password):
        self.password = passlib.hash.sha512_crypt.hash(password)
        db.session.commit()

    # for oauth
    def get_user_id(self):
        return self.id

@login_manager.user_loader
def user_loader(id):
    return User.query.get(id)

def getUserId(name, password):
    u = User.query.filter_by(name=name).first()
    if not u:
        return None
    if not u.checkPassword(password):
        return None
    return user_loader(u.id)

def setPW(user, oldone, newone):
    if not user.checkPassword(oldone):
        return "Wrong password"
    if len(newone) < 8:
       return "Password should be more than 8 characters"
    user.setPassword(newone)
    user.passtime = time.time()
    db.session.commit()
    return "ok"

def add_user(name, passwd='', time=0, admin=0):
    logger.info("Add User " + name)
    u = User.query.filter_by(name=name).first()
    assert(not u)
    u = User(name=name,
             passtime=time,
             admin=admin)
    u.setPassword(passwd)
    db.session.add(u)
    db.session.commit()
    return name
