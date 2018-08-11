import os
from flask import Flask
from .routes import bp
from .models import db, login_manager
from .box import bp as boxbp


def create_app(config={}):
    app = Flask(__name__)
    app.config.update(config)
    app.register_blueprint(bp, url_prefix='')
    app.register_blueprint(boxbp, url_prefix='/box/')

    db.init_app(app)
    login_manager.init_app(app)

    return app
