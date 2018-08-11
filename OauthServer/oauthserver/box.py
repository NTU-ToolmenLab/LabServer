from flask import Blueprint, request, session
from flask import render_template, redirect, jsonify, url_for
import flask_login
import logging

logger = logging.getLogger('oauthserver')
bp = Blueprint(__name__, 'box')

@bp.route('/list')
@flask_login.login_required
def boxLists():
    return render_template('boxlist.html', container_list = [])
