from flask import Blueprint, request, abort, render_template, redirect, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
import flask_login
import logging

logger = logging.getLogger('oauthserver')
bp = Blueprint(__name__, 'box')
db = SQLAlchemy()

@bp.route('/')
@flask_login.login_required
def Lists():
    lists = getList()
    return render_template('boxlist.html', container_list = lists)

@bp.route('/api', methods=['POST'])
@flask_login.login_required
def api():
    nowUser = flask_login.current_user
    data = request.form
    logger.debug(nowUser.name + " api " + str(data))

    # box = Box.query.filter_by(user=nowUser.name).filter(
    #       Box.docker_id.startswith(data['id'])).first()
    box = Box.query.filter_by(user=nowUser.name).first()
    if not box:
        abort(501)

    if data.get('method') == 'Resume':
        box.resume()
        # return redirect("/vnc/?token=" + token)
    elif data.get('method') == 'Stop':
        box.stop()
    elif data.get('method') == 'Restart':
        box.restart()
    else:
        abort(501)
    return redirect(url_for('oauthserver.box.Lists'))

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

    def __str__(self):
        return '<Box {}>'.format(docker_name)

    def getStatus(self):
        example = {'id'    : "id",
                   'name'  : "name",
                   'text'  : "text",
                   'status': "status"}
        return example

    def resume(self):
        pass

    def restart(self):
        pass

    def stop(self):
        pass

def add_box(user, docker_name, box_name=''):
    logger.info("Add box " + user + ' -> ' + docker_name)
    if not box_name:
        box_name = docker_name
    assert(not Box.query.filter_by(
        docker_name = docker_name,
        user = user).first())

    # no check for user is exist or not
    # assert(User.query.filter_by(name=user).first())

    box = Box(user=user,
              docker_name=docker_name,
              box_name=box_name)
    db.session.add(box)
    db.session.commit()

def getList():
    nowUser = flask_login.current_user
    logger.info("list " + nowUser.name)
    boxes_ori = Box.query.filter_by(user=nowUser.name).all()
    return [box.getStatus() for box in boxes_ori]
