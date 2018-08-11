from flask import Blueprint, request, session
from flask import render_template, redirect, jsonify

bp = Blueprint(__name__, 'home')

@bp.route('/', methods=('GET', 'POST'))
def Login():
    return render_template('Login.html')

