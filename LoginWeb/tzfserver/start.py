import os
import sys
from urllib.parse import urlparse
from functools import wraps

from flask import Flask, redirect, request, render_template, session, abort, Response, make_response
from flask import url_for as flask_url
from datetime import timedelta

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils

app = Flask(__name__)
app.secret_key = ''  # Change this!
app.config['SAML_PATH'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'saml')

from .dbOp  import *
from .Login import *
from . import admin_page

login_manager.init_app(app)
login_manager.login_view = 'Login'

def raw_url_for(a):
    return "https://my.domain.ntu.edu.tw:443" + a

def url_for(a): # bugs, When you add pathstrip or use https withous 443
    return raw_url_for(flask_url(a))

def init_saml_auth(req):
    auth = OneLogin_Saml2_Auth(req, custom_base_path=app.config['SAML_PATH'])
    return auth

def prepare_flask_request(request):
    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields
    url_data = urlparse(request.url)
    return {
        'https': 'on',
        'http_host': request.host,
        'server_port': url_data.port,
        'script_name': request.path,
        'get_data': request.args.copy(),
        # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
        # 'lowercase_urlencoding': True,
        'post_data': request.form.copy()
    }

def getUser():
    if 'samlUserdata' in session:
        if len(session['samlUserdata']) > 0:
            return user_loader(session['samlUserdata']['uid'][0])
    return None

def isLogin(func):
    @wraps(func)
    def wrap_func(*arg, **kwargs):
        nowUser = getUser()
        if not nowUser:
            return redirect(url_for('Login'))
        return func(nowUser)
    return wrap_func

@app.route('/', methods=['GET', 'POST'])
def Login():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    errors = []

    if 'sso' in request.args:
        return redirect(auth.login(return_to=url_for('Lists')))

    elif 'acs' in request.args:
        auth.process_response()
        errors = auth.get_errors()
        if len(errors) == 0:
            session['samlUserdata'] = auth.get_attributes()
            session['samlNameId'] = auth.get_nameid()
            session['samlSessionIndex'] = auth.get_session_index()
            return redirect(url_for('Lists'))
            # self_url = OneLogin_Saml2_Utils.get_self_url(req)
            # if 'RelayState' in request.form and self_url != request.form['RelayState']:
            #    return redirect(auth.redirect_to(request.form['RelayState']))
        app.logger.error(errors)

    elif 'sls' in request.args:
        dscb = lambda: session.clear()
        url = auth.process_slo(delete_session_cb=dscb)
        errors = auth.get_errors()
        if len(errors) == 0:
            if url is not None:
                return redirect(url)
    elif 'slo' in request.args:
        name_id = None
        session_index = None
        if 'samlNameId' in session:
            name_id = session['samlNameId']
        if 'samlSessionIndex' in session:
            session_index = session['samlSessionIndex']
        return redirect(auth.logout(
            name_id=name_id, session_index=session_index,
            return_to=url_for('Login')))

    nowUser = getUser()
    if not nowUser:
        return render_template('Login.html')
    else:
        return redirect(url_for('Lists'))

@app.route('/metadata/')
def metadata():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if len(errors) == 0:
        resp = make_response(metadata, 200)
        resp.headers['Content-Type'] = 'text/xml'
    else:
        resp = make_response(', '.join(errors), 500)
    return resp

@app.route('/lists')
@isLogin
def Lists(nowUser):
    lists = nowUser.user.lists()
    return render_template('lists.html', container_list = lists)

@app.route('/apis', methods=['POST'])
@isLogin
def apis(nowUser):
    nowUser = nowUser.user
    data = request.form
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
@isLogin
def Resume(nowUser):
    cid = request.form.get('id')
    token = nowUser.user.resume(cid)
    # https://github.com/containous/traefik/issues/1957
    # BUG: solution: hard code beacuse of the bug
    # return redirect("/vnc/?tokeon=" + token)
    return redirect("https://" + request.host + "/vnc/?path=vnc/?token=" + token)

@app.route("/changepw", methods=['GET', 'POST'])
@isLogin
def ChangePassword(nowUser):
    if request.method == 'GET':
        return render_template('changePassword.html')
    oldone = request.form.get("opw")
    newone = request.form.get("npw")
    if newone != request.form.get("npw1"):
        return render_template('changePassword.html', error="confirm password error")

    rep = setPW(nowUser, oldone, newone)
    if rep != "ok":
        return render_template('changePassword.html', error=rep)

    return redirect(url_for('Lists'))

@app.route("/vnctoken", methods=['GET'])
@isLogin
def tokenVnc(nowUser):
    token = request.args.get('token')
    return nowUser.user.checkVNCtoken(token)

@app.route('/adminpage', methods=['GET', 'POST'])
@isLogin
def adminPage(nowUser):
    if not nowUser.user.isadmin:
        raise UserError
    if request.method == 'GET':
        return admin_page.adminPage()
    else:
        return admin_page.adminPageModify(request.form)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
