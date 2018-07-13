from flask import render_template
import passlib.hash
from .dbOp import set_db, query_db
from .ContainerServer import *

def adminPage():
    alltokens = query_db("SELECT * FROM tokens ORDER BY user", one=False)
    allusers  = query_db("SELECT * FROM login ORDER BY name", one=False)

    return render_template('adminpage.html', tables = [
        { "name": "tokens", "table": alltokens},
        { "name": "login",  "table": allusers} ])

def adminPageModify(form):
    # init
    table = ''
    key   = ''
    if form['table'] == 'tokens':
        key = 'tokenname'
        keywords = ["tokenname", "user", "boxname"]
    elif form['table'] == 'login':
        key = 'name'
        keywords = ["name", "pass", "time", "admin"]
    else:
        return adminPage()

    # parse form
    table = form['table']
    formwords = {i:form[i].strip() for i in keywords}

    # special
    if table == 'login':
        formwords['pass'] = passlib.hash.sha512_crypt.encrypt(formwords['pass'])
        formwords['time'] = 0
        formwords['admin'] = int(formwords['admin'])

    if form['method'] == 'add':
        set_db("INSERT INTO {} ({}) VALUES ({})".format(
                table, ",".join(keywords), ",".join(['?'] * len(keywords))),
               tuple(formwords.values()))
    elif form['method'] == 'delete':
        set_db("DELETE FROM " + table + " WHERE " + key + " = ?", (formwords[key],))
    else:
        return adminPage()

    return adminPage()
