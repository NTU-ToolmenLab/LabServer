from flask import request, abort, render_template, redirect, url_for
import flask_login
import logging
import time
import re
from .models import db as user_db, User
from .box_models import db as db, Box, Image, bp, otherAPI
from labboxmain import celery
import shutil
import os


logger = logging.getLogger('labboxmain')


@bp.route('/')
@flask_login.login_required
def List():
    return render_template('boxlist.html',
                           container_list=getList(),
                           create_param=getCreate(),
                           image_list=getImages())


@bp.route('/vnctoken', methods=['POST'])
@flask_login.login_required
def vncToken():
    now_user = flask_login.current_user
    docker_name = request.form.get('token')
    if not docker_name:
        abort(403)
    if now_user.groupid == 1:
        box = Box.query.filter_by(docker_name=docker_name).first()
    else:
        box = Box.query.filter_by(user=now_user.name,
                                  docker_name=docker_name).first()
    if not box:
        abort(403)
    return bp.vncpw


@bp.route('/api', methods=['POST'])
@flask_login.login_required
def api():
    now_user = flask_login.current_user
    data = request.form
    logger.debug('[API] ' + now_user.name + ': ' + str(data))

    if not data.get('name'):
        abort(403, 'What is your environment name')
    if now_user.groupid == 1:
        box = Box.query.filter_by(docker_name=data['name']).first()
    else:
        box = Box.query.filter_by(user=now_user.name,
                                  docker_name=data['name']).first()
    if not box:
        abort(403, 'Cannot find your environment')

    # OK
    if data.get('method') == 'Desktop':
        return redirect('/vnc/?path=vnc/?token=' + box.docker_name)

    elif data.get('method') == 'Jupyter':
        return redirect('/jupyter/' + box.docker_name)

    elif data.get('method') == 'Restart':
        box.api('restart')

    elif data.get('method') == 'Delete':
        box.api('delete', check=False)
        imageDelete.delay(box.id)

    elif data.get('method') == 'node':
        if not data.get('node') or data.get('node') not in getNodes():
            abort(403, 'No such server')
        box.commit(check=False)
        box.api('delete', check=False)
        changeNode.delay(box.id, now_user.id, data['node'])

    elif data.get('method') == 'Stop':
        boxStop(box)

    elif data.get('method') == 'Rescue':
        box.api('delete', check=False)

        image = box.image if not box.getImage() else box.getBackupname()
        rescue.delay(box.id, now_user.id, image)

    elif data.get('method') == 'Sync':
        if not Box.query.filter_by(user=now_user.name,
                                   box_name=box.parent).first():
            abort(403, 'No Parent existed')
        box.api('delete', check=False)
        parent_box = Box.query.filter_by(user=now_user.name,
                                         box_name=box.parent).first()
        backupname = parent_box.getBackupname()
        parent = box.parent
        node = box.node
        name = box.box_name
        realname = box.docker_name
        duplicate.delay(parent_box.id, now_user.id, name, node,
                        realname, backupname, box.id)

    else:
        abort(403, 'How can you show this error')

    return redirect(url_for('labboxmain.box_models.List'))


@bp.route('/create', methods=['POST'])
@flask_login.login_required
def create():
    now_user = flask_login.current_user
    data = request.form
    logger.debug('[API Create] ' + now_user.name + ': ' + str(data))

    if now_user.use_quota >= now_user.quota:
        abort(403, 'Quota = 0')
    if not data.get('node') or data.get('node') not in getNodes():
        abort(403, 'No such server')
    image = data.get('image')
    parent = None
    if Image.query.filter_by(user='user', name=image).first():
        image = bp.images + data.get('image')
    elif Box.query.filter_by(user=now_user.name, box_name=image).first():
        parent = Box.query.filter_by(user=now_user.name, box_name=image).first()
        image = parent.getBackupname()
    else:
        abort(403, 'No such environment')

    realname = now_user.name + '{:.3f}'.format(time.time()).replace('.', '')
    name = realname

    if data.get('name'):
        name = now_user.name + '_' + data['name']
        # https://github.com/tg123/sshpiper/blob/3243906a19e2e63f7a363050843109aa5caf6b91/sshpiperd/upstream/workingdir/workingdir.go#L36
        if not re.match(r'^[a-z_][-a-z0-9_]{0,31}$', name):
            abort(403, 'Your name does not follow the rule')
    if Box.query.filter_by(box_name=name).first():
        abort(403, 'Already have environment')
    if Box.query.filter_by(docker_name=realname).first():
        abort(403, 'Already have environment')

    if parent:
        logger.debug('[Duplicate] ' + now_user.name + ': ' + name + ' from ' + parent.box_name)
        duplicate.delay(parent.id,
                        now_user.id, name, data['node'], realname, image)
    else:
        createAPI(now_user.id, name, data['node'], realname, image)
    return redirect(url_for('labboxmain.box_models.List'))


def createAPI(userid, name, node, realname, image, pull=True, parent=''):
    now_user = User.query.get(userid)
    now_dict = {
        'name': realname,
        'node': node,
        'image': image,
        'pull': pull,
        'parent': parent,
        'labnas': 'True',
        'homepath': now_user.name}
    now_dict.update(bp.create_rule(now_user))

    rep = otherAPI('create', **now_dict)

    # async, wait for creation
    box = Box(box_name=name,
              user=now_user.name,
              docker_name=now_dict['name'],
              image=now_dict['image'],
              parent=parent,
              node=now_dict['node'],
              box_text='Creating')
    db.session.add(box)
    db.session.commit()

    # user
    now_user.use_quota += 1
    user_db.session.commit()
    boxWaitCreate.delay(box.id, now_user.id)


@celery.task()
def boxWaitCreate(bid, uid):
    box = Box.query.get(bid)
    now_user = User.query.filter_by(name=box.user).first()
    logger.debug('[API Create] wait: ' + box.box_name)
    for i in range(60 * 10):  # 10 min
        time.sleep(1)
        rep = otherAPI('search', name=box.docker_name, check=False)
        if str(rep['status']).lower() == 'running':
            break
    else:
        logger.error('[API Create] fail: ' + box.box_name)
        box.box_text = 'Cannot start your environment'
        db.session.commit()
        raise TimeoutError

    logger.debug('[API Create] success: ' + box.box_name)
    box.docker_ip = rep['ip']
    box.docker_id = rep['id']
    box.box_text = ''
    db.session.commit()
    piperCreate(box.box_name, box.docker_ip)

    # make sure it is running
    time.sleep(5)
    box.api('passwd', pw=now_user.password)


# Setting up creating options
def getList():
    now_user = flask_login.current_user
    if now_user.groupid == 1:
        boxes_ori = Box.query.all()
    else:
        boxes_ori = Box.query.filter_by(user=now_user.name).all()
    boxes = [box.getStatus() for box in boxes_ori]
    return boxes


def getCreate():
    now_user = flask_login.current_user
    return {'quota': now_user.quota, 'use_quota': now_user.use_quota,
            'image': [i['name'] for i in getImages()], 'node': getNodes()}


def getImages():
    images = Image.query.filter_by(user='user').order_by(Image.id.desc()).all()
    images = [{'name': i.name, 'description': i.description} for i in images]

    now_user = flask_login.current_user
    box_images = Box.query.filter_by(user=now_user.name).all()
    images.extend([{'name': i.box_name} for i in box_images])
    return images


def getNodes():
    if not bp.usek8s:
        return ['server']
    req = otherAPI('listnode', check=False)
    nodes = [i['name'] for i in req]
    return nodes


# Routine
@celery.task()
def routineMaintain():
    # Commit
    logger.info('[Routine] Commit')
    boxes = Box.query.all()
    for box in boxes:
        logger.debug('[Routine] Commit: ' + box.box_name)
        box.commit(check=False)

    # check if it is somewhat kill by kubernetes
    logger.info('[Routine] check inconsistence')
    statusTarget = 'Not Consist ID'
    for box in boxes:
        if box.getStatus()['status'] == statusTarget:
            logger.warning('[Routine] inconsistence ID: ' + box.box_name)
            rep = otherAPI('search', name=box.docker_name, check=False)
            box.docker_ip = rep['ip']
            box.docker_id = rep['id']
            db.session.commit()

    # run passwd
    logger.info('[Routine] passwd')
    users = User.query.all()
    for user in users:
        boxsPasswd(user)

    # Maintain sshpiper
    logger.info('[Routine] sshpiper')
    for name in os.listdir(bp.sshpiper):
        if os.path.isdir(bp.sshpiper + name):
            shutil.rmtree(bp.sshpiper + name)
    for box in boxes:
        if box.getStatus()['status'] == 'running':
            piperCreate(box.box_name, box.docker_ip)


# Change password for all boxes
def boxsPasswd(now_user):
    boxes = Box.query.filter_by(user=now_user.name).all()
    for box in boxes:
        if box.getStatus()['status'] == 'running':
            box.api('passwd', pw=now_user.password)


# There are three type of operation is time-consuming
# * Create (Download Image and start container)
# * Backup (Upload Image)
# * Delete (Delete pod in k8s)

# Devices:      piper database k8s Docker Image Registry
# createAPI       *      *      *    *
# Delete(API)                   *    *
# piperDelete     *
# boxDelete       *      *
# envDelete       *      *
# imageDelete     *      *      *
# commit(API)                               *
# boxpush                                          *
# boxStop         *             *    *      *
# Rescue          = Delete(API) + envDelete + createAPI
# changeNode      = commit(API) + boxPush + Delete(API) + imageDelete + CreateAPI
# duplicate+Sync  = commit(API) + boxPush + Delete(API) + envDelete + CreateAPI
def boxPush(bid):
    box = Box.query.get(bid)
    if not bp.registry_user:
        boxDelete(box)
        return

    box.box_text = 'Backuping'
    db.session.commit()
    try:
        otherAPI('push', name=box.getBackupname(),
                         docker_node=box.node,
                         **bp.registry_user)
    except Exception as e:
        box.box_text = 'Backup Error'
        db.session.commit()
        raise e

    box.box_text = ''
    db.session.commit()


def boxStop(box):
    box.commit()
    box.api('delete', check=False)
    piperDelete(box.box_name)
    box.box_text = 'Stopped'
    db.session.commit()


def stopAll(node='all'):
    # Commit
    logger.warning('[Waring] Stop ' + node)
    if node != 'all':
        boxes = Box.query.filter_by(node=node).all()
    else:
        boxes = Box.query.all()
    for box in boxes:
        if box.getStatus()['status'] == 'running':
            logger.debug('[Warning] Stop: ' + box.box_name)
            boxStop(box)


def piperCreate(name, ip):
    sshfolder = bp.sshpiper + name + '/'
    sshpip = sshfolder + 'sshpiper_upstream'
    os.makedirs(sshfolder, exist_ok=True)
    open(sshpip, 'w').write('ubuntu@' + ip)
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


def envDelete(bid):
    box = Box.query.get(bid)
    box.box_text = 'Deleting ENV'
    db.session.commit()
    logger.debug('[API Delete] wait: ' + box.box_name)
    for i in range(60 * 10):  # 10 min
        time.sleep(1)
        rep = otherAPI('search', name=box.docker_name, check=False)
        if str(rep['status']) == '404':
            break
    else:
        logger.error('[API Delete] fail: ' + box.box_name)
        box.box_text = 'Delete again later or Cannot Delete'
        db.session.commit()
        # do not delte in database if cannot delete it in real world.
        raise TimeoutError

    logger.debug('[API Delete] success: ' + box.box_name)
    boxDelete(box)


@celery.task()
def imageDelete(bid):
    box = Box.query.get(bid)
    box.box_text = 'Deleting ENV copy'
    db.session.commit()
    otherAPI('deleteImage', name=box.getBackupname(), docker_node=box.node, check=False)
    envDelete(bid)


@celery.task()
def rescue(bid, uid, image):
    box = Box.query.get(bid)
    node = box.node
    name = box.box_name
    parent = box.parent
    docker_name = box.docker_name
    logger.debug('[rescue] envDelete: ' + name)
    envDelete(bid)
    logger.debug('[rescue] create: ' + name)
    createAPI(uid, name, node, docker_name, image, pull=False, parent=parent)


@celery.task()
def changeNode(bid, uid, node):
    box = Box.query.get(bid)
    parent = box.parent
    name = box.box_name
    docker_name = box.docker_name
    backupname = box.getBackupname()

    logger.debug('[Changenode] push:' + name)
    boxPush(bid)
    logger.debug('[Changenode] envDelete: ' + name)
    imageDelete(bid)
    logger.debug('[Changenode] create: ' + name)
    createAPI(uid, name, node, docker_name, backupname, parent=parent)


@celery.task()
def duplicate(bid, uid, name, node, docker_name, image, delete_bid=''):
    box = Box.query.get(bid)
    logger.debug('[Duplicate] push:' + box.box_name)
    box.commit(check=False)
    boxPush(bid)
    if delete_bid:
        logger.debug('[Duplicate] envDelete: ' + name)
        envDelete(delete_bid)
    logger.debug('[Duplicate] create: ' + name)
    createAPI(uid, name, node, docker_name, image, parent=box.box_name)
