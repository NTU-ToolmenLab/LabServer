from flask import Blueprint, request, abort, render_template, redirect, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
import flask_login
import logging
from requests import post

logger = logging.getLogger('oauthserver')
bp = Blueprint(__name__, 'box')
db = SQLAlchemy()

myMap = {
    'Resume' : "start",
    'Stop'   : "stop",
    'Restart': "restart"}

# to get app config
@bp.record
def record_params(setup_state):
    bp.sock = setup_state.app.config['dockerserver']

@bp.route('/')
@flask_login.login_required
def List():
    lists = getList()
    return render_template('boxlist.html', container_list = lists)

@bp.route('/api', methods=['POST'])
@flask_login.login_required
def api():
    nowUser = flask_login.current_user
    data = request.form
    logger.debug(nowUser.name + " api " + str(data))

    if nowUser.admin:
        box = Box.query.filter_by(docker_id=data['id']).first()
    else:
        box = Box.query.filter_by(user=nowUser.name, docker_id=data['id']).first()

    if not box:
        abort(403)
    if data.get('method') not in myMap.keys():
        abort(403)

    logger.info("boxapi " + nowUser.name + " " + data['method'] + " " + data['id'])
    box.api(myMap[data['method']])
    if data.get('method') == 'Resume':
        if not nowUser.admin or box.user == nowUser.name:
            box.api('passwd', pw=nowUser.password)

        return redirect("/vnc/?path=vnc/?token=" + box.docker_name) # on docker
    return redirect(url_for('oauthserver.box.List'))

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
        print(self.box_name)
        # test without dockerserver
        # return {'name'  : self.box_name,
        #         'id': 'erro',
        #         'status': 'error'}
        rep = post(bp.sock + "/search", data={'key': self.docker_name}).json()
        if rep.get('error'):
            return {'name'  : self.box_name,
                    'id': 'error',
                    'status': 'error'}

        self.docker_id = rep['id']
        self.docker_ip = rep['ip']
        return {'id'    : self.docker_id,
                'name'  : self.box_name,
                'text'  : self.box_text,
                'status': rep['status']}

    def api(self, name, **kwrags):
        if name not in ['start', 'restart', 'stop', 'passwd']:
            abort(403)

        rep = post(bp.sock + "/" + name, data={'id': self.docker_id, **kwrags}).json()
        if rep.get('error'):
            abort(403)

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
    if nowUser.admin:
        boxes_ori = Box.query.all()
    else:
        boxes_ori = Box.query.filter_by(user=nowUser.name).all()
    boxes = [box.getStatus() for box in boxes_ori]
    db.session.commit()
    return boxes
