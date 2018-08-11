from flask import Blueprint, request, session
from flask import render_template, redirect, jsonify, url_for
import flask_login
from .models import getUserId, setPW
import logging
from .adminpage import adminSet, adminView

logger = logging.getLogger('oauthserver')
bp = Blueprint(__name__, 'home')

@bp.route('/', methods=('GET', 'POST'))
def Login():
    if request.method == 'GET':
        if flask_login.login_fresh():
            logger.debug("Skip Login")
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
    logger.info(name + " Login")
    user = getUserId(name, password)
    if not user:
        logger.info(name + " Login Fail")
        return None
    flask_login.login_user(user)
    return user

@bp.route("/logout")
@flask_login.login_required
def Logout():
    nowUser = flask_login.current_user
    logger.info(nowUser.name + " Logout")
    flask_login.logout_user()
    return redirect(url_for('oauthserver.routes.Login'))

@bp.route("/passwd", methods=['GET', 'POST'])
@flask_login.login_required
def ChangePassword():
    if request.method == 'GET':
        return render_template('changePassword.html')
    nowUser = flask_login.current_user
    logger.info(nowUser.name + " ChangePassword")
    oldone = request.form.get("opw")
    newone = request.form.get("npw")

    rep = "ok"
    if newone != request.form.get("npw1"):
        rep = "confirm password error"
    if rep == "ok":
        rep = setPW(nowUser, oldone, newone)
    if rep != "ok":
        logger.info(nowUser.name + " ChangePassword Fail With " + rep)
        return render_template('changePassword.html', error=rep)

    logger.info(nowUser.name + " ChangePassword OK")
    return redirect(url_for('oauthserver.routes.hi'))

@bp.route("/adminpage", methods=['GET', 'POST'])
@flask_login.login_required
def AdminPage():
    nowUser = flask_login.current_user
    # if nowUser.admin
    logger.info(nowUser.name + " AdminPage")
    if request.method == 'GET':
        return adminView()
    else:
        return adminSet(request.form)

    return redirect(url_for('oauthserver.routes.Login'))
