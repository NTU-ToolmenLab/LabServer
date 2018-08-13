from flask import render_template
from .models import User, db as userdb
from .box import Box, db as boxdb


def adminView():
    alluser = [{ k: v for k, v in dict(a.__dict__).items() if not k.startswith('_')}
        for a in User.query.all()]
    allbox = [{ k: v for k, v in dict(a.__dict__).items() if not k.startswith('_')}
        for a in Box.query.all()]
    return render_template('adminpage.html', tables = [
        { "name": "user",  "table": alluser},
        { "name": "box",  "table": allbox} ])

def adminSet(form):
    # parse form
    if form.get('table') not in ['user', 'box']:
        return adminView()
    formwords = {i:form[i].strip() for i in form if i not in ['table', 'method']}

    if form['table'] == 'user':
        cls = User
        db = userdb
    elif form['table'] == 'box':
        cls = Box
        db = boxdb

    acls = cls.query.filter_by(id=int(formwords['id'])).first()
    if form['method'] == 'delete':
        db.session.delete(acls)
        db.session.commit()
    elif form['method'] == 'add':
        modify = 1
        if not acls:
            acls = cls()
            modify = 0
        print(cls.__table__.columns.items())
        for i in cls.__table__.columns.items():
            if i[0] == 'password':
                acls.setPassword(formwords[i[0]])
            else:
                setattr(acls, i[0], i[1].type.python_type(formwords[i[0]]))
        if not modify:
            db.session.add(acls)
        db.session.commit()
    return adminView()
