from flask import request, abort, render_template, redirect, url_for
import flask_login
import logging
import time
import re
from .models import db as user_db, User
from .box_models import db as db, Box, Image, bp, otherAPI
from oauthserver import celery
import shutil
import os


logger = logging.getLogger('oauthserver')


@bp.route('/')
@flask_login.login_required
def List():
    return render_template('boxlist.html',
                           container_list=getList(),
                           create_param=getCreate(),
                           image_list=getImages())


@bp.route('/api', methods=['POST'])
@flask_login.login_required
def api():
    nowUser = flask_login.current_user
    data = request.form
    logger.debug(nowUser.name + " api " + str(data))

    if not data.get('name'):
        abort(403, 'What is your environment name')
    if nowUser.groupid == 1:
        box = Box.query.filter_by(docker_name=data['name']).first()
    else:
        box = Box.query.filter_by(user=nowUser.name,
                                  docker_name=data['name']).first()
    if not box:
        abort(403, 'Cannot find your environment')

    # OK
    logger.info("boxapi " + nowUser.name + " " + data['method'] + " " + data['name'])
    backupname = bp.backup + box.docker_name

    if data.get('method') == 'Start':
        box.api('start')
        if nowUser.groupid != 1 or box.user == nowUser.name:
            box.api('passwd', pw=nowUser.password)
        return redirect("/vnc/?path=vnc/?token=" + box.docker_name)  # on docker

    elif data.get('method') == 'Restart':
        box.api('restart')

    elif data.get('method') == 'Delete':
        box.api('delete', check=False)
        imageDelete.delay(box.id, backupname)

    elif data.get('method') == 'node':
        if not data.get('node') or data.get('node') not in getNodes():
            abort(403, 'No such server')
        box.commit(check=False)
        box.api('delete', check=False)
        changeNode.delay(box.id, nowUser.id,
                         box.box_name,
                         data['node'],
                         box.docker_name,
                         backupname)

    elif data.get('method') == 'Stop':
        box.commit(check=False)
        box.api('delete', check=False)
        piperDelete(box.box_name)

    elif data.get('method') == 'Rescue':
        box.api('delete', check=False)

        image = box.image if not box.getImage() else backupname
        rescue.delay(box.id, nowUser.id,
                     box.box_name,
                     box.node,
                     box.docker_name,
                     image)

    else:
        abort(403, 'How can you show this error')

    return redirect(url_for('oauthserver.box_models.List'))


@bp.route('/create', methods=['POST'])
@flask_login.login_required
def create():
    nowUser = flask_login.current_user
    data = request.form
    logger.debug(nowUser.name + " create " + str(data))

    if not data.get('image'):
        abort(403, 'No such environment')
    if nowUser.use_quota >= nowUser.quota:
        abort(403, 'Quota = 0')
    if not data.get('node') or data.get('node') not in getNodes():
        abort(403, 'No such server')

    realname = nowUser.name + str(time.time()).replace('.', '')
    name = realname

    if Image.query.filter_by(user='user', name=data.get('image')).first():
        image = bp.images + data.get('image')
    else:
        abort(403, 'No such environment')
    if data.get('name'):
        name = nowUser.name + '_' + data['name']
        # https://github.com/tg123/sshpiper/blob/3243906a19e2e63f7a363050843109aa5caf6b91/sshpiperd/upstream/workingdir/workingdir.go#L36
        if not re.match(r'^[a-z_][-a-z0-9_]{0,31}$', name):
            abort(403, 'Your name does not follow the rule')
    if Box.query.filter_by(box_name=name).first():
        abort(403, 'Already have environment')
    if Box.query.filter_by(docker_name=realname).first():
        abort(403, 'Already have environment')

    createAPI.delay(nowUser.id, name, data.get('node'), realname, image)
    return redirect(url_for('oauthserver.box_models.List'))


@celery.task()
def createAPI(nowUser, name, node, realname, image):
    homepath = nowUser.name
    labnas = 'True'

    rep = otherAPI('create',
                   name=realname,
                   node=node,
                   image=image,
                   homepath=homepath,
                   labnas=labnas,
                   homenas='True')

    # async, wait for creation
    box = Box(box_name=name,
              docker_name=realname,
              user=nowUser.name,
              image=image,
              box_text='Creating',
              node=node)
    db.session.add(box)
    db.session.commit()

    # user
    nowUser.use_quota += 1
    user_db.session.commit()
    boxCreate.delay(box.id)


@bp.route('/vnctoken', methods=['POST'])
@flask_login.login_required
def vncToken():
    nowUser = flask_login.current_user
    docker_name = request.args.get('token')
    if nowUser.groupid == 1:
        box = Box.query.filter_by(docker_name=docker_name).first()
    else:
        box = Box.query.filter_by(user=nowUser.name,
                                  docker_name=docker_name).first()
    if not box:
        abort(403)
    return "password_of_vnc"


def getList():
    nowUser = flask_login.current_user
    logger.info("list " + nowUser.name)
    if nowUser.groupid == 1:
        boxes_ori = Box.query.all()
    else:
        boxes_ori = Box.query.filter_by(user=nowUser.name).all()
    boxes = [box.getStatus() for box in boxes_ori]
    return boxes


def getCreate():
    nowUser = flask_login.current_user
    images = [i.name for i in getImages()]
    return {'quota': nowUser.quota, 'use_quota': nowUser.use_quota,
            'image': images, 'node': getNodes()}


def getImages():
    images = Image.query.filter_by(user='user').order_by(Image.id.desc()).all()
    return images


def getNodes():
    # return ['n1', 'n2', 'n3'] # test
    if not bp.usek8s:
        return ['server']
    req = otherAPI('listnode', check=False)
    nodes = [i['name'] for i in req]
    return nodes


def piperCreate(name, ip):
    sshfolder = bp.sshpiper + name + '/'
    sshpip = sshfolder + "sshpiper_upstream"
    os.makedirs(sshfolder, exist_ok=True)
    open(sshpip, "w").write("ubuntu@" + ip)
    os.chmod(sshpip, 0o600)


def piperDelete(name):
    shutil.rmtree(bp.sshpiper + name, ignore_errors=True)


def boxDelete(box):
    u = User.query.filter_by(name=box.user).first()
    piperDelete(box.box_name)
    db.session.delete(box)
    db.session.commit()

    # u.use_quota -= 1
    u.use_quota = Box.query.filter_by(user=u.name).count()
    user_db.session.commit()


# run commit every day
@celery.task()
def goCommit():
    logger.debug("Commit now")
    boxes = Box.query.all()
    for box in boxes:
        logger.debug("Commit " + box.box_name)
        box.commit(check=False)


# There are three type of operation is time-consuming
# Create (Download Image and start container)
# Backup (Upload Image)
# Delete (Delete pod in k8s)

# Delete is also Problem
# method:      piper env image database additional
# api Delete          *
# piperDelete    *
# boxDelete      *                *
# envDelete      *    *
# rescue         *    *                   +create
# imageDelete    *    *    *      *
# boxpush        *    *    *      *       +push (no commmit here)
# entry:Delete   *    *    *      *
# entry:Stop     *    *
# entry:Rescue   *    *
@celery.task()
def boxCreate(id):
    box = Box.query.get(id)
    for i in range(60 * 10):  # 10 min
        time.sleep(1)
        rep = otherAPI('search', name=box.docker_name, check=False)
        if str(rep['status']).lower() == 'running':
            break
    else:
        box.box_text = 'Cannot start your environment'
        db.session.commit()
        raise TimeoutError

    box.docker_ip = rep['ip']
    box.docker_id = rep['id']
    box.box_text = ''
    db.session.commit()

    piperCreate(box.box_name, box.docker_ip)


def boxPush(id, backupname):
    box = Box.query.get(id)
    if not bp.registry_user:
        boxDelete(box)
        return

    box.box_text = 'Backuping'
    db.session.commit()
    try:
        otherAPI('push', name=backupname, docker_node=box.node, **bp.registry_user)
    except Exception as e:
        box.box_text = str("Backup Error")
        db.session.commit()
        raise e

    imageDelete.delay(id, backupname)


@celery.task()
def imageDelete(id, backupname):
    box = Box.query.get(id)
    box.box_text = 'Deleting ENV copy'
    db.session.commit()
    otherAPI('deleteImage', name=backupname, docker_node=box.node, check=False)
    envDelete(id)


def envDelete(id):
    box = Box.query.get(id)
    box.box_text = 'Deleting ENV'
    db.session.commit()
    for i in range(60 * 10):  # 10 min
        time.sleep(1)
        rep = otherAPI('search', name=box.docker_name, check=False)
        if str(rep['status']) == '404':
            break
    else:
        box.box_text = 'Delete again later or Cannot Delete'
        db.session.commit()
        # do not delte in database if cannot delete it in real world.
        raise TimeoutError

    boxDelete(box)


# Can not chain?
# ugly method
@celery.task()
def rescue(bid, uid, name, node, docker_name, image):
    logger.debug("rescue - envDelete", name)
    envDelete(bid)
    logger.debug("rescue - create", name)
    createAPI(uid, name, node, docker_name, image)


# ugly method
@celery.task()
def changeNode(bid, uid, name, node, docker_name, backupname):
    logger.debug("Changenode - push", name)
    boxPush(bid, backupname)
    logger.debug("Changenode - envDelete", name)
    envDelete(bid)
    logger.debug("Changenode - create", name)
    createAPI(uid, name, node, docker_name, backupname)
