from flask import Blueprint, request, session
from flask import render_template, redirect, jsonify, url_for
import flask_login
from .models import getUserId


bp = Blueprint(__name__, 'home')

@bp.route('/', methods=('GET', 'POST'))
def Login():
    if request.method == 'GET':
        if flask_login.login_fresh():
            return redirect(url_for('oauthserver.routes.hi'))
        else:
            return render_template('Login.html')
    else:
        user = requestParse(request)
        if user:
            return redirect(url_for('oauthserver.routes.hi'))
        else:
            return render_template('Login.html', error="Fail to Login")

@bp.route("/api/hi")
@flask_login.login_required
def hi():
    return jsonify({"hi":True})

def requestParse(request):
    name     = request.form.get('userName')
    password = request.form.get('userPassword')
    user = getUserId(name, password)
    if not user:
        return None
    flask_login.login_user(user)
    return user
