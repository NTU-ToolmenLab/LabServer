from flask import request, abort, render_template, redirect, url_for, jsonify
import flask_login
import logging
import time
import datetime
from .models import User
from .box_models import db as db, Box, Image, bp, otherAPI
from labboxmain import celery
from .box import otherAPI, getImages


logger = logging.getLogger('labboxmain')


class BoxQueue(db.Model):
    __tablename__ = 'boxqueue'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(32), nullable=False)
    image = db.Column(db.String(64), nullable=False)
    command = db.Column(db.String(128))
    queueing = db.Column(db.Boolean, default=True)
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __str__(self):
        return '<BoxQueue {}>'.format(name)

    def getName(self):
        return 'queue-' + str(self.id)

    def getData(self):
        return {'name': self.getName(),
                'user': self.user,
                'image': self.image.split(':')[-1],
                'queueing': self.queueing,
                'date': (self.create_date + datetime.timedelta(hours=8)).
                         strftime('%Y/%m/%d %X')}

    def getLog(self):
        rep = otherAPI('search', name=self.getName(), check=False)
        print(rep)
        log = otherAPI('log', name=self.getName(), check=False)
        print(log)
        return {'node': rep['node'],
                'start_time': rep['start'],
                'command': self.command,
                **log}

    def run(self, node):
        node = getFreeNode()
        now_user = User.query.filter_by(name=self.user).first()

        now_dict = {
            'name': self.getName(),
            'node': node,
            'image': self.image,
            'command': self.command,
            'pull': True,
            'labnas': 'True',
            'homepath': now_user.name}
        now_dict.update(bp.create_rule(now_user))
        rep = otherAPI('create', **now_dict)

        self.queueing = False
        db.session.commit()


@bp.route('/queue', methods=['GET', 'POST'])
@flask_login.login_required
def queueAppend():
    now_user = flask_login.current_user
    if request.method == 'GET':
        return show()

    data = request.form
    logger.debug('[Queue] ' + now_user.name + ': ' + str(data))

    if not data.get('command'):
        abort(403, 'What is your command')
    if len(data['command']) >= 128:
        abort(403, 'Command Too Long')
    image = data.get('image')
    parent = None
    if Image.query.filter_by(user='user', name=image).first():
        image = bp.images + data.get('image')
        """
    elif Box.query.filter_by(user=now_user.name, box_name=image).first():
        parent = Box.query.filter_by(user=now_user.name, box_name=image).first()
        image = parent.getBackupname()
        box.commit(check=False)
        boxPush(box.id)
    """
    else:
        abort(403, 'No such environment')

    boxqueue = BoxQueue(user=now_user.name,
                        image=image,
                        command=data['command'])
    db.session.add(boxqueue)
    db.session.commit()
    return show()


@bp.route('/log', methods=['POST'])
@flask_login.login_required
def log():
    now_user = flask_login.current_user
    data = request.form
    box = BoxQueue.query.filter_by(user=now_user.name,
                                   id=int(data.get('name').split('-')[1])).first()
    if not box:
        abort(403, 'Not your command')

    # TODO
    return jsonify(box.getLog())


@bp.route('/queueDelete', methods=['POST'])
@flask_login.login_required
def queueDelete():
    now_user = flask_login.current_user
    data = request.form
    box = BoxQueue.query.filter_by(user=now_user.name,
                                   id=int(data.get('name').split('-')[1])).first()
    if not box:
        abort(403, 'Not your queue')
    otherAPI('delete', name=box.getName(), check=False)
    db.session.delete(box)
    db.session.commit()
    return show()


def show():
    queue = [box.getData() for box in BoxQueue.query.all()]
    return render_template('box_avail.html',
                           queue=queue,
                           create_images=[i['name'] for i in getImages()])


# TODO
def findFreeNode():
    box.run('lab304-server3')
