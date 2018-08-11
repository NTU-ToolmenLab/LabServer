from flask import render_template
from .models import User, db


def adminView():
    allusers = User.query.all()
    alluser = [
        { k: v for k, v in dict(a.__dict__).items() if not k.startswith('_')}
        for a in allusers ]
    return render_template('adminpage.html', tables = [
        { "name": "user",  "table": alluser} ])

def adminSet(form):
    # parse form
    if form['table'] != 'user':
        return adminView()
    formwords = {i:form[i].strip() for i in form if i not in ['table', 'method']}

    cls = User
    acls = cls.query.filter_by(id=int(formwords['id'])).first()
    if form['method'] == 'delete':
        db.session.delete(acls)
        db.session.commit()
    elif form['method'] == 'add':
        modify = 1
        if not acls:
            acls = cls()
            modify = 0
        for i in cls.__table__.columns.items():
            if i[0] == 'password':
                setattr(acls, i[0], i[1].type.python_type(formwords[i[0]]))
            else:
                acls.setPassword(formwords[i[0]])
        if not modify:
            db.session.add(acls)
        db.session.commit()
    return adminView()
