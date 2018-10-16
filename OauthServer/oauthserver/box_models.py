from flask import Blueprint, abort
from flask_sqlalchemy import SQLAlchemy
import logging
from requests import post


db = SQLAlchemy()
logger = logging.getLogger('oauthserver')
bp = Blueprint(__name__, 'box')


# to get app config
@bp.record
def record_params(setup_state):
    if setup_state.app.config.get('myapik8s'):
        bp.sock = setup_state.app.config.get('myapik8s')
        bp.usek8s = True
    else:
        bp.sock = setup_state.app.config['dockerserver']


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

    def __str__(self):
        return '<Box {}>'.format(docker_name)

    def getStatus(self):
        # TODO update before get status
        return {'name': self.box_name,
                'node': self.node,
                'image': self.image,
                'status': 'Testing'}

    def api(self, name, **kwrags):
        if name not in ['start', 'restart', 'stop', 'passwd', 'delete']:
            abort(403)

        if bp.usek8s:
            if name == 'stop':
                abort(403)

        if bp.usek8s:
            if name == 'delete': # not handle in dockerServer
                url = bp.sock + '/delete'
            else:
                url = bp.sock + '/{}/{}'.format(self.node, name)
            rep = post(url, data={'name': self.docker_name, **kwrags}).json()
        else:
            rep = post(bp.sock + "/" + name,
                    data={'id': self.docker_id, **kwrags}).json()

        if rep.get('error'):
            abort(403)


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
