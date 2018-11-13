from flask import request, abort, render_template, redirect, jsonify, url_for
import flask_login
import logging
import requests
import time
import re
from .models import db as user_db, User
from .box_models import db as db, Box, Image, bp
import shutil
import os


logger = logging.getLogger('oauthserver')

myMap = {
    'Start' : "start",
    'Stop'   : "stop",
    'Delete' : "delete",
    'Restart': "restart"}

@bp.route('/')
@flask_login.login_required
def List():
    return render_template('boxlist.html',
            container_list = getList(),
            create_param = getCreate(), 
            image_list = getImages())

@bp.route('/api', methods=['POST'])
@flask_login.login_required
def api():
    nowUser = flask_login.current_user
    data = request.form
    logger.debug(nowUser.name + " api " + str(data))

    if not data.get('name'):
        abort(403)

    if nowUser.admin:
        box = Box.query.filter_by(docker_name=data['name']).first()
    else:
        box = Box.query.filter_by(user=nowUser.name, docker_name=data['name']).first()

    if not box:
        abort(403)
    if data.get('method') not in myMap.keys():
        abort(403)

    logger.info("boxapi " + nowUser.name + " " + data['method'] + " " + data['name'])
    box.api(myMap[data['method']])

    # special case
    if data.get('method') == 'Start':
        if not nowUser.admin or box.user == nowUser.name:
            box.api('passwd', pw=nowUser.password)
        return redirect("/vnc/?path=vnc/?token=" + box.docker_name) # on docker

    elif data.get('method') == 'Delete':
        u = User.query.filter_by(name=box.user).first()
        u.use_quota -= 1
        db.session.delete(box)
        user_db.session.commit()
        db.session.commit()
        piperDelete(box.box_name)

    return redirect(url_for('oauthserver.box_models.List'))

@bp.route('/create', methods=['POST'])
@flask_login.login_required
def create():
    nowUser = flask_login.current_user
    data = request.form
    logger.debug(nowUser.name + " create " + str(data))

    if not data.get('image') or not data.get('node'):
        abort(403)
    if not Image.query.filter_by(user='user', name=data.get('image')).first():
        abort(403)
    if nowUser.use_quota >= nowUser.quota:
        abort(403)
    if not data.get('node') or data.get('node') not in getNodes():
        abort(403)

    realname = nowUser.name + str(time.time()).replace('.','')
    name = realname

    if data.get('name'):
        name = nowUser.name + '_' + data['name']
        # https://github.com/tg123/sshpiper/blob/3243906a19e2e63f7a363050843109aa5caf6b91/sshpiperd/upstream/workingdir/workingdir.go#L36
        if not re.match(r'^[a-z_][-a-z0-9_]{0,31}$', name):
            abort(403)
        if Box.query.filter_by(box_name=name).first():
            abort(403)

    rep = requests.post(bp.sock + '/create', data={
        'name': realname,
        'node': data.get('node'),
        'image': bp.imagehub + data.get('image'),
        'homepath': nowUser.name,
        'labnas': 'True',
        'homenas': 'True'}).json()
    if str(rep['status']) != '200':
        abort(409, str(rep))

    for i in range(60):
        time.sleep(1) # wait for create
        rep = requests.post(bp.sock + '/search', data={'name': realname}).json()
        if rep['status'].lower() == 'running':
            break
    else:
        abort(409)

    box = Box(box_name=name,
              docker_ip=rep['ip'],
              docker_name=realname,
              docker_id=rep['id'],
              user=nowUser.name,
              image=data.get('image'),
              node=data.get('node'))
    db.session.add(box)
    db.session.commit()

    nowUser.use_quota += 1
    user_db.session.commit()

    piperCreate(box.box_name, box.docker_ip)

    return redirect(url_for('oauthserver.box_models.List'))

@bp.route('/vnctoken', methods=['POST'])
@flask_login.login_required
def vncToken():
    nowUser = flask_login.current_user
    docker_name = request.args.get('token')
    if nowUser.admin:
        box = Box.query.filter_by(docker_name=docker_name).first()
    else:
        box = Box.query.filter_by(user=nowUser.name, docker_name=docker_name).first()
    if not box:
        abort(403)
    return "password_of_vnc"



def getList():
    nowUser = flask_login.current_user
    logger.info("list " + nowUser.name)
    if nowUser.admin:
        boxes_ori = Box.query.all()
    else:
        boxes_ori = Box.query.filter_by(user=nowUser.name).all()
    boxes = [box.getStatus() for box in boxes_ori]
    db.session.commit()
    return boxes

def getCreate():
    nowUser = flask_login.current_user
    images = [i.name for i in Image.query.filter_by(user='user').all()]
    return {'quota': nowUser.quota, 'use_quota': nowUser.use_quota, 
            'image': images, 'node': getNodes()}

def getImages():
    return Image.query.filter_by(user='user').all()

def getNodes():
    # return ['n1', 'n2', 'n3'] # test
    if not bp.usek8s:
        return ['server']
    req = requests.get(bp.sock + '/listnode').json()
    nodes = [i['name'] for i in req]
    return nodes

def piperCreate(name, ip):
    sshfolder = bp.sshpiper + name + '/'
    sshpip =  sshfolder + "sshpiper_upstream"
    os.makedirs(sshfolder, exist_ok=True)
    open(sshpip, "w").write("ubuntu@" + ip)
    os.chmod(sshpip, 0o600)

def piperDelete(name):
    shutil.rmtree(bp.sshpiper + name, ignore_errors=True)
