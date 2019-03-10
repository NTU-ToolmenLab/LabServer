from flask import Blueprint, abort, render_template
from flask_sqlalchemy import SQLAlchemy
import logging
from requests import post
import datetime


db = SQLAlchemy()
logger = logging.getLogger('oauthserver')
bp = Blueprint(__name__, 'box')


# to get app config
@bp.record
def record_params(setup_state):
    config = setup_state.app.config
    if config.get('myapik8s'):
        bp.sock = config.get('myapik8s')
        bp.usek8s = True
    else:
        bp.sock = config.get('dockerserver')
        bp.usek8s = False
    bp.images = config.get('registry_images')
    bp.backup = config.get('registry_backup')
    bp.sshpiper = config.get('sshpiper')

    if config.get('registry_password'):
        bp.registry_user = dict(
            username=config.get('registry_user'),
            password=config.get('registry_password'),
            registry=config.get('registry_url'))
    else:
        bp.registry_user = None


@bp.errorhandler(403)
def userForbidden(e):
    return render_template('error.html', code=403, text=e.description), 403


@bp.errorhandler(500)
def serverError(e):
    return render_template('error.html', code=500, text=e.description), 500


class Box(db.Model):
    __tablename__ = 'box'
    id = db.Column(db.Integer, primary_key=True)
    box_name = db.Column(db.String(32), nullable=False)
    box_text = db.Column(db.String(256))
    docker_ip = db.Column(db.String(32))  # add after creation
    docker_name = db.Column(db.String(32), nullable=False)
    docker_id = db.Column(db.String(64))  # add after creation
    # relationship is not very helpful to my project
    # user = db.relationship('User')
    # user.name
    user = db.Column(db.String(32), nullable=False)
    node = db.Column(db.String(32), nullable=False)
    image = db.Column(db.String(64), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __str__(self):
        return '<Box {}>'.format(docker_name)

    def getStatus(self):
        status = self.box_text
        if not status:
            rep = otherAPI('search', name=self.docker_name, check=False)
            status = str(rep['status']).lower()
            if status == 'running' and self.docker_ip != rep['ip']:
                # self.docker_ip = rep['ip']
                # self.docker_id = rep['id']
                # db.session.commit()
                status = 'Not Consist IP'

        return {'name': self.box_name,
                'realname': self.docker_name,
                'node': self.node,
                'date': (self.date + datetime.timedelta(hours=8)
                        ).strftime('%Y/%m/%d %X'),
                'image': self.image.split(':')[-1],
                'status': status}

    def api(self, method, check=True, **kwargs):
        """
        There are many mothods:
        start, stop, delete, restart, passwd, rescue
        """
        # deal with url
        name = self.docker_name
        base_url = bp.sock
        if bp.usek8s:
            # Not handle in dockerserver for k8s
            if method != 'delete':
                name = self.docker_id
                base_url = bp.sock + '/{}'.format(self.node)

            # deal with methods
            if method == 'stop':
                self.commit(check=False)
                self.api('delete')
                return

            # rescue
            if method == 'rescue':
                self.api('delete')
                return

        url = base_url + '/' + method

        if method == 'delete':
            check = False

        rep = post(url, data={'name': name, **kwargs}).json()

        if check and str(rep.get('status')) != '200':
            logger.error("ERROR " + url + str(kwargs) + str(rep))
            abort(500, 'Server API error')

        return rep

    def commit(self, **kwargs):
        self.api('commit', newname=bp.backup + self.docker_name, **kwargs)
        self.api('prune', check=False)


class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    user = db.Column(db.String(32), nullable=False)
    description = db.Column(db.String)

    def __str__(self):
        return '<Image {}>'.format(self.name)


def otherAPI(method, docker_node=None, check=True, **kwargs):
    """
    There are many mothods:
    push, deleteImage, search, create, listnode, searchimage
    """
    base_url = bp.sock
    if bp.usek8s and method in ['push', 'deleteImage', 'searchimage']:
        base_url = bp.sock + '/{}'.format(docker_node)
    url = base_url + '/' + method
    rep = post(url, data=kwargs).json()

    if check and str(rep.get('status')) != '200':
        logger.error("ERROR " + url + str(kwargs) + str(rep))
        abort(500, 'Server API error')

    return rep


def add_box(user, docker_name, box_name, image, node=''):
    logger.info("Add box " + user + ' -> ' + docker_name)
    assert(not Box.query.filter_by(docker_name=docker_name,
                                   user=user).first())

    # no check for user is exist or not
    # assert(User.query.filter_by(name=user).first())

    box = Box(user=user,
              docker_name=docker_name,
              box_name=box_name,
              image=image,
              node=node)
    db.session.add(box)
    db.session.commit()


def add_image(user, name, description=''):
    logger.info('Add image ' + user + ' -> ' + name)
    assert(not Image.query.filter_by(name=name,
                                     user=user).first())

    image = Image(name=name, user=user, description=description)
    db.session.add(image)
    db.session.commit()
