import os
from flask import Flask
from .routes import bp
from .models import db, login_manager
from .box import bp as boxbp, db as boxdb
from .oauth2 import config_oauth


def create_app(config={}):
    app = Flask(__name__)
    app.config.update(config)
    app.register_blueprint(bp, url_prefix='')
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "oauthserver.routes.Login" # redir

    config_oauth(app)
    os.environ['AUTHLIB_INSECURE_TRANSPORT']=1

    # box
    app.register_blueprint(boxbp, url_prefix='/box/')
    boxdb.init_app(app)
    return app
