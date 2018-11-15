from flask import Blueprint, abort
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


class Box(db.Model):
    __tablename__ = 'box'
    id = db.Column(db.Integer, primary_key=True)
    box_name = db.Column(db.String(32), nullable=False)
    box_text = db.Column(db.String(256))
    docker_ip = db.Column(db.String(32)) # add in runtime
    docker_name = db.Column(db.String(32), nullable=False)
    docker_id = db.Column(db.String(64)) # add in runtime
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
        rep = post(bp.sock + '/search', data={'name': self.docker_name}).json()
        return {'name': self.box_name,
                'realname': self.docker_name,
                'node': self.node,
                'date': (self.date + datetime.timedelta(hours=8)).strftime('%Y/%m/%d %X'),
                'image': self.image.split(':')[-1],
                'status': str(rep['status']).lower()}

    def api(self, method, check=True, **kwargs):
        # deal with url
        name = self.docker_name
        base_url = bp.sock
        if bp.usek8s:
            if method != 'delete': # delete not handle in dockerserver
                name = self.docker_id
                base_url = bp.sock + '/{}'.format(self.node)
        url = base_url + '/' + method

        # deal with methods
        if bp.usek8s or True: # test
            if method == 'stop':
                self.commit(check=False)
                self.api('delete')
                return

        if 'name' in kwargs:
            name = kwargs['name']
            del kwargs['name']
        rep = post(url, data={'name': name, **kwargs}).json()

        if method == 'delete': # not need to check
            check = False
        if check and str(rep.get('status')) != '200':
            abort(409)

    def commit(self, **kwargs):
        self.api('commit', newname=bp.backup + self.docker_name, **kwargs)
        self.api('prune')


class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    user = db.Column(db.String(32), nullable=False)
    description = db.Column(db.String)

    def __str__(self):
        return '<Image {}>'.format(self.name)


def add_box(user, docker_name, box_name, image, node=''):
    logger.info("Add box " + user + ' -> ' + docker_name)
    assert(not Box.query.filter_by(
        docker_name = docker_name,
        user = user).first())

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
    assert(not Image.query.filter_by(
        name = name,
        user = user).first())

    image = Image(name=name, user=user, description=description)
    db.session.add(image)
    db.session.commit()
