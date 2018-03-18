import sqlite3
import flask
from .start import app

DATABASE = 'database.db'

def get_db():
    db = getattr(flask.g, '_database', None)
    if db is None:
        db = flask.g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    with app.app_context():
        cur = get_db().execute(query, args)
        if one:
            rv = cur.fetchone()
        else:
            rv = cur.fetchall()
        cur.close()
        return rv

def set_db(query, args):
    with app.app_context():
        cur = get_db()
        cur.execute(query, args)
        cur.commit()
        cur.close()
