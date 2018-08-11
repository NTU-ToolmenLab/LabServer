from flask import render_template
from .models import User, db


def adminView():
    allusers = User.query.all()
    alluser = [
        { k: v for k, v in dict(a.__dict__).items() if not k.startswith('_')}
        for a in allusers ]
    return render_template('adminpage.html', tables = [
        { "name": "login",  "table": alluser} ])

def adminSet(form):
    pass
