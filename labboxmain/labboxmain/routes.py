from flask import (Blueprint, request, session,
                   abort, render_template, redirect, jsonify, url_for)
import flask_login
import logging
from urllib.parse import urlparse, urljoin

from .models import getUserId, setPW
from .adminpage import adminSet, adminView

logger = logging.getLogger('labboxmain')
bp = Blueprint(__name__, 'home')


# http://flask.pocoo.org/snippets/62/
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


@bp.route('/', methods=['GET', 'POST'])
def Login():
    if request.method == 'GET':
        if flask_login.login_fresh():
            return redirect(url_for('labboxmain.box_models.List'))
        else:
            return render_template('Login.html')
    else:
        user = requestParse(request)
        if user:
            nexturl = request.args.get('next')
            if not is_safe_url(nexturl):
                return abort(400)
            logger.info("[Login] " + user.name)
            return redirect(nexturl or url_for('labboxmain.box_models.List'))
        else:
            logger.warning("[Login] fail " + user.name)
            return render_template('Login.html', error="Fail to Login")


@bp.route("/help")  # help web
@flask_login.login_required
def help():
    return render_template('help.html')


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
    now_user = flask_login.current_user
    logger.info(now_user.name + " Logout")
    flask_login.logout_user()
    return redirect(url_for('labboxmain.routes.Login'))


@bp.route("/passwd", methods=['GET', 'POST'])
@flask_login.login_required
def ChangePassword():
    if request.method == 'GET':
        return render_template('changePassword.html')
    now_user = flask_login.current_user
    logger.info(now_user.name + " ChangePassword")
    oldone = request.form.get("opw")
    newone = request.form.get("npw")

    rep = "ok"
    if newone != request.form.get("npw1"):
        rep = "confirm password error"
    if rep == "ok":
        rep = setPW(now_user, oldone, newone)
    if rep != "ok":
        logger.info(now_user.name + " ChangePassword Fail With " + rep)
        return render_template('changePassword.html', error=rep)

    logger.info("[passwd] " + now_user.name)
    # ugly import
    from .box import boxsPasswd
    boxsPasswd(now_user)
    logger.info(now_user.name + " ChangePassword OK")
    return redirect(url_for('labboxmain.box_models.List'))


@bp.route("/adminpage", methods=['GET', 'POST'])
@flask_login.login_required
def AdminPage():
    now_user = flask_login.current_user
    if now_user.groupid != 1:
        abort(401)
    logger.warning("[Admin] " + now_user.name)
    if request.method == 'GET':
        return adminView()
    else:
        return adminSet(request.form)

    return redirect(url_for('labboxmain.routes.Login'))
