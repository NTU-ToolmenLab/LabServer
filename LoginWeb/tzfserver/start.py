from flask import Flask, redirect, url_for, request, render_template, session
import json
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

from .dbOp  import *
from .Login import *

login_manager.init_app(app)
login_manager.login_view = 'Login'
bcrypt.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def Login():
    if request.method == 'GET':
        if flask_login.login_fresh():
            return redirect(url_for('Lists'))
        else:
            return render_template('Login.html')
    else:
        if requestParse(request):
            return redirect(url_for('Lists'))
        else:
            return render_template('Login.html', error="Fail to Login")

@app.route("/logout")
@flask_login.login_required
def Logout():
    flask_login.logout_user()
    return redirect(url_for('Login'))

@app.route('/lists')
@flask_login.login_required
def Lists():
    lists = flask_login.current_user.user.lists()
    return render_template('lists.html', container_list = lists)

@app.route('/apis', methods=['POST'])
@flask_login.login_required
def apis():
    data = request.get_json()
    nowUser = flask_login.current_user.user
    if data['method'] == 'Resume':
        nowUser.resume(data['id'])
    elif data['method'] == 'Restart':
        nowUser.restart(data['id'])
    elif data['method'] == 'Reset':
        nowUser.reset(data['id'])
    elif data['method'] == 'Remove':
        nowUser.remove(data['id'])
    else:
        print("Error")
        pass # unknown
    return redirect(url_for('Lists'))

@app.route("/resume", methods=['POST'])
@flask_login.login_required
def Resume():
    cid = request.form.get('id')
    nowUser = flask_login.current_user.user
    token = nowUser.resume(cid)
    return redirect("/vnc/?token=" + token)

"""
@app.before_request
def before_request():
    # app.permanent_session_lifetime = timedelta(days=1)
    app.permanent_session_lifetime = timedelta(seconds=10)
"""

# one time
def init_db():
    """ usage: import start; start.init_db(); """
    with app.app_context():
        db = get_db()
        with app.open_resource('schema_login.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

if __name__=='__main__':
    app.run()
