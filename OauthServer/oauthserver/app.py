import os
from flask import Flask
import logging
from werkzeug.contrib.fixers import ProxyFix
from .routes import bp
from .models import db, login_manager
from .box import bp as boxbp, db as boxdb, goCommit
from .oauth2 import config_oauth
from apscheduler.schedulers.background import BackgroundScheduler


def create_app(config={}):
    app = Flask(__name__)
    app.debug = True
    config['registry_images'] = config.get('registry_url') + '/' +  \
                                config.get('registry_images') + ':'
    config['registry_backup'] = config.get('registry_url') + '/' +  \
                                config.get('registry_backup') + ':'
    app.config.update(config)
    app.config.update({'SCHEDULER_API_ENABLED': True})
    app.register_blueprint(bp, url_prefix='')
    db.init_app(app)
    login_manager.init_app(app)
    config_oauth(app)
    setLog(app)

    login_manager.login_view = "oauthserver.routes.Login"  # redir
    app.wsgi_app = ProxyFix(app.wsgi_app)
    # os.environ['AUTHLIB_INSECURE_TRANSPORT'] = "1"

    scheduler = BackgroundScheduler()
    scheduler.add_job(goCommit, "interval", [app], **config['commit_interval'])
    scheduler.start()

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
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
