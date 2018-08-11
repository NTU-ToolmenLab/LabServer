import os
from flask import Flask
from .routes import bp


def create_app(config=None):
    app = Flask(__name__)
    # db.init_app(app)
    app.register_blueprint(bp, url_prefix='')
    return app

