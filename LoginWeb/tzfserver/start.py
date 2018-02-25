from flask import Flask, redirect, request, render_template, session, abort
from flask import url_for as flask_url
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

from .dbOp  import *
from .Login import *

login_manager.init_app(app)
login_manager.login_view = 'Login'
bcrypt.init_app(app)

def url_for(a): # bugs, When you add pathstrip or use https withous 443
    return "https://127.0.0.1:443" + flask_url(a)

@app.route('/', methods=['GET', 'POST'])
def Login():
    if request.method == 'GET':
        if flask_login.login_fresh():
            return redirect(url_for('Lists'))
        else:
            return render_template('Login.html')
    else:
        if requestParse(request):
            if request.form['userPassword'] == 'test': # change it
                # You can ignore change password. fine
                return redirect(url_for("ChangePassword"))
            else:
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
    data = request.form
    nowUser = flask_login.current_user.user
    if data.get('method') == 'Stop':
        nowUser.stop(data['id'])
    elif data.get('method') == 'Restart':
        nowUser.restart(data['id'])
    # elif data['method'] == 'Reset':
    #    nowUser.reset(data['id'])
    else:
        abort(404)
        pass # unknown
    return redirect(url_for('Lists'))

@app.route("/resume", methods=['POST'])
@flask_login.login_required
def Resume():
    cid = request.form.get('id')
    nowUser = flask_login.current_user.user
    token = nowUser.resume(cid)
    # https://github.com/containous/traefik/issues/1957
    # BUG: solution: hard code beacuse of the bug
    # return redirect("/vnc/?tokeon=" + token)
    return redirect("https://" + request.host + "/vnc/?token=" + token)

@app.route("/changepw", methods=['GET', 'POST'])
@flask_login.login_required
def ChangePassword():
    if request.method == 'GET':
        return render_template('changePassword.html')
    nowUser = flask_login.current_user
    oldone = request.form.get("opw")
    newone = request.form.get("npw")
    if newone != request.form.get("npw1"):
        return render_template('changePassword.html', error="confirm password error")

    rep = setPW(nowUser, oldone, newone)
    if rep != "ok":
        return render_template('changePassword.html', error=rep)

    return redirect(url_for('Lists'))


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

# one time
def add():
    """ usage: from tzfserver import start; start.add()"""
    # all import from Login
    name = std_add_user()
    std_add_token(name)

if __name__=='__main__':
    app.run()
