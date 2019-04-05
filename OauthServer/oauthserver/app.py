import os
from flask import Flask
import logging
from werkzeug.middleware.proxy_fix import ProxyFix
from .routes import bp
from .models import db, login_manager
from .oauth2 import config_oauth
from celery import Celery


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
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)
    # os.environ['AUTHLIB_INSECURE_TRANSPORT'] = "1"

    # redis
    celery = make_celery(app)
    return app, celery


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['celery_result_backend'],
        broker=app.config['celery_broker_url']
    )
    celery.conf.beat_schedule = app.config['celery_schedule']
    # celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


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
