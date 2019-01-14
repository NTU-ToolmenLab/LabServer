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
myMap = {
    'Start': "start",
    'Stop': "stop",
    'Delete': "delete",
    'Restart': "restart"}


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
    if nowUser.admin:
        box = Box.query.filter_by(docker_name=data['name']).first()
    else:
        box = Box.query.filter_by(user=nowUser.name,
                                  docker_name=data['name']).first()
    if not box:
        abort(403, 'Cannot find your environment')
    if data.get('method') not in myMap.keys():
        abort(403, 'How can you show this error')

    logger.info("boxapi " + nowUser.name + " " + data['method'] + " " + data['name'])
    box.api(myMap[data['method']])

    # special case
    backupname = bp.backup + box.docker_name
    if data.get('method') == 'Start':
        if not nowUser.admin or box.user == nowUser.name:
            box.api('passwd', pw=nowUser.password)
        return redirect("/vnc/?path=vnc/?token=" + box.docker_name)  # on docker

    elif data.get('method') == 'Stop':
        boxPush.delay(box.id, backupname)

    elif data.get('method') == 'Delete':
        # delete database before really deleted it
        Image.query.filter_by(user=box.user, name=box.docker_name).delete()
        db.session.commit()
        imageDelete.delay(box.id, backupname)

    return redirect(url_for('oauthserver.box_models.List'))


@bp.route('/create', methods=['POST'])
@flask_login.login_required
def create():
    nowUser = flask_login.current_user
    data = request.form
    logger.debug(nowUser.name + " create " + str(data))

    if not data.get('image'):
        abort(403, 'No such environment')
    if not data.get('node'):
        abort(403, 'No such server')
    if nowUser.use_quota >= nowUser.quota:
        abort(403, 'Quota = 0')
    if not data.get('node') or data.get('node') not in getNodes():
        abort(403, 'No such server')

    realname = nowUser.name + str(time.time()).replace('.', '')
    name = realname
    image = ''

    if Image.query.filter_by(user='user', name=data.get('image')).first():
        image = bp.images + data.get('image')
    elif Image.query.filter_by(user=nowUser.name, name=data.get('image')).first():
        image = bp.backup + data.get('image')
        name = realname = data.get('image')
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

    rep = otherAPI('create',
                   name=realname,
                   node=data.get('node'),
                   image=image,
                   homepath=nowUser.name,
                   labnas='True',
                   homenas='True')

    # async, wait for creation
    box = Box(box_name=name,
              docker_name=realname,
              user=nowUser.name,
              image=image,
              box_text='Creating',
              node=data.get('node'))
    db.session.add(box)
    db.session.commit()
    boxCreate.delay(box.id)

    # user
    nowUser.use_quota += 1
    user_db.session.commit()
    return redirect(url_for('oauthserver.box_models.List'))


@bp.route('/vnctoken', methods=['POST'])
@flask_login.login_required
def vncToken():
    nowUser = flask_login.current_user
    docker_name = request.args.get('token')
    if nowUser.admin:
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
    if nowUser.admin:
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
    nowUser = flask_login.current_user
    if nowUser.admin:
        return Image.query.all()
    else:
        images = Image.query.filter_by(user='user').all()
        images.extend(Image.query.filter_by(user=nowUser.name).all())
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
    u.use_quota -= 1
    db.session.delete(box)
    user_db.session.commit()
    db.session.commit()
    piperDelete(box.box_name)


# run commit every day
@celery.task()
def goCommit():
    logger.debug("Commit now")
    boxes = Box.query.all()
    for box in boxes:
        st = box.getStatus()
        if str(st['status']).lower() == 'running':
            box.commit()


# There are three type of operation is time-consuming
# Create (Download Image and start container)
# Backup (Upload Image)
# Delete (Delete pod in k8s)
@celery.task()
def boxCreate(id):
    box = Box.query.get(id)
    for i in range(60 * 10):  # 10 min
        time.sleep(1)
        rep = otherAPI('search', name=box.docker_name, check=False)
        if rep['status'].lower() == 'running':
            break
    else:
        abort(500, 'Cannot start your environment')

    box.docker_ip = rep['ip']
    box.docker_id = rep['id']
    box.box_text = ''
    db.session.commit()

    piperCreate(box.box_name, box.docker_ip)


# After stop, the pod is deleted
# Now, you push to image to registy and delete the image
@celery.task()
def boxPush(id, backupname):
    box = Box.query.get(id)
    if not bp.registry_user:
        boxDelete(box)
        return

    box.box_text = 'Backuping'
    db.session.commit()
    try:
        otherAPI('push', name=backupname, node=box.node, **bp.registry_user)
        Image.query.filter_by(user=box.user, name=box.docker_name).delete()
        image = Image(name=box.docker_name, user=box.user,
                      description="Stopped " + box.box_name)
        db.session.add(image)
        db.session.commit()
    except Exception as e:
        box.box_text = str("Backup Error")
        db.session.commit()
        return
    imageDelete.delay(id, backupname)


@celery.task()
def imageDelete(id, backupname):
    box = Box.query.get(id)
    box.box_text = 'Deleting ENV copy'
    db.session.commit()
    otherAPI('deleteImage', name=backupname, node=box.node, check=False)

    box.box_text = 'Deleting ENV'
    db.session.commit()
    for i in range(60 * 10):  # 10 min
        time.sleep(1)
        rep = otherAPI('search', name=box.docker_name, check=False)
        if str(rep['status']) == '404':
            break
    else:  # do not delte in database if cannot delete it in real world.
        return

    boxDelete(box)
