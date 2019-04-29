from flask import (Blueprint, request, session,
                   abort, render_template, redirect, jsonify, url_for)
import flask_login
import logging
from urllib.parse import urlparse, urljoin

from .models import getUserId, setPW
from .adminpage import adminSet, adminView
from .oauth2 import authorization, OAuth2Client, clientCreate, require_oauth
from authlib.flask.oauth2 import current_token

logger = logging.getLogger('oauthserver')
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
            logger.debug("Skip Login")
            return redirect(url_for('oauthserver.box_models.List'))
        else:
            return render_template('Login.html')
    else:
        user = requestParse(request)
        if user:
            nexturl = request.args.get('next')
            logger.debug("Login with url " + str(nexturl))
            if not is_safe_url(nexturl):
                return abort(400)
            return redirect(nexturl or url_for('oauthserver.box_models.List'))
        else:
            return render_template('Login.html', error="Fail to Login")


# for test
@bp.route("/api/hi")
@flask_login.login_required
def hi():
    return jsonify({'hi': True})


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

    # ugly import
    from .box import boxsPasswd
    boxsPasswd(nowUser)
    logger.info(nowUser.name + " ChangePassword OK")
    return redirect(url_for('oauthserver.box_models.List'))


@bp.route("/adminpage", methods=['GET', 'POST'])
@flask_login.login_required
def AdminPage():
    nowUser = flask_login.current_user
    if nowUser.groupid != 1:
        abort(401)
    logger.info(nowUser.name + " AdminPage")
    if request.method == 'GET':
        return adminView()
    else:
        return adminSet(request.form)

    return redirect(url_for('oauthserver.routes.Login'))


# oauth2
@bp.route('/oauth/client', methods=['GET', 'POST'])
@flask_login.login_required
def client():
    nowUser = flask_login.current_user
    if nowUser.groupid != 1:
        abort(401)
    logger.debug("[oauth] client " + nowUser.name)

    if request.method == 'GET':
        return render_template('clients.html', clients=OAuth2Client.query.all())
    clientCreate(request.form, nowUser)
    return render_template('clients.html', clients=OAuth2Client.query.all())


@bp.route('/oauth/authorize')
@flask_login.login_required
def authorize():
    """
    Need to ask grant and confirmed again, but I'm lazy
    # grant = authorization.validate_consent_request(end_user=user)
    """
    logger.debug("[oauth] auth " + str(request.form))
    nowUser = flask_login.current_user
    grant = authorization.validate_consent_request(end_user=nowUser)
    return authorization.create_authorization_response(grant_user=nowUser)


@bp.route('/oauth/token', methods=['POST'])
def issue_token():
    logger.debug("[oauth] token " + str(request.form))
    return authorization.create_token_response()


@bp.route('/oauth/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_endpoint_response('revocation')


@bp.route('/oauth/profile', methods=['GET'])
@require_oauth('profile')
def profile():
    user = current_token.user
    name = user.name
    logger.debug("[oauth] user " + name)
    return jsonify({
        'id': name,
        'username': name,
        'name': name,
        'email': name + '@my.domain.ntu.edu.tw'})
