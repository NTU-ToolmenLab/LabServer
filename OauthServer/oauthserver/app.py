import os
from flask import Flask
import logging
from .routes import bp
from .models import db, login_manager
from .box import bp as boxbp, db as boxdb
from .oauth2 import config_oauth


def create_app(config={}):
    app = Flask(__name__)
    app.debug=True
    app.config.update(config)
    app.register_blueprint(bp, url_prefix='')
    db.init_app(app)
    login_manager.init_app(app)
    config_oauth(app)
    setLog(app)

    login_manager.login_view = "oauthserver.routes.Login" # redir
    app.wsgi_app = ReverseProxied(app.wsgi_app, app.config.get('PREFERRED_URL_SCHEME'))
    # os.environ['AUTHLIB_INSECURE_TRANSPORT'] = "1"

    # box
    app.register_blueprint(boxbp, url_prefix='/box/')
    boxdb.init_app(app)
    return app

def setLog(app):
    logger = logging.getLogger('oauthserver')
    logger.setLevel(logging.DEBUG)

    # output to std
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # output to file
    if app.config.get("logfile"):
        fh = logging.FileHandler(app.config['logfile'])
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # authlib logger
    if app.debug:
        logger = logging.getLogger('authlib')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(ch)


class ReverseProxied(object):
    def __init__(self, app, http):
        self.app = app
        self.http = http

    def __call__(self, environ, start_response):
        environ['wsgi.url_scheme'] = self.http
        return self.app(environ, start_response)
