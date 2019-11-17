from flask import request, abort, render_template, redirect, url_for, jsonify
import flask_login
import logging
import time
import datetime
import requests
from .models import User
from .box_models import db as db, Box, Image, bp, otherAPI
from labboxmain import celery
from .box import otherAPI, getImages, boxPush


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
                'command': self.command,
                'queueing': self.queueing,
                'date': (self.create_date + datetime.timedelta(hours=8)).
                         strftime('%Y/%m/%d %X')}

    def getLog(self):
        rep = otherAPI('search', name=self.getName(), check=False)
        log = otherAPI('log', name=self.getName(), check=False)
        if log.get('result'):
            log['running_time(s)'] = log['result'][1] - log['result'][0]
            del log['result']
        return {'node': rep['node'],
                'start_time': rep['start'],
                **log}

    def run(self, nodegpu):
        now_user = User.query.filter_by(name=self.user).first()
        node, gpu = nodegpu

        now_dict = {
            'name': self.getName(),
            'node': node,
            'gpu': gpu,
            'image': self.image,
            'command': self.command,
            'pull': True,
            'labnas': 'True',
            'homepath': now_user.name}
        now_dict.update(bp.create_rule(now_user))
        rep = otherAPI('create', **now_dict)

        self.queueing = False
        bp.r_cli.set(str(nodegpu), time.time())
        db.session.commit()


@bp.route('/queue', methods=['GET', 'POST'])
@flask_login.login_required
def queue():
    now_user = flask_login.current_user
    if request.method == 'GET':
        queue = []
        for box in BoxQueue.query.all():
            q = box.getData()
            q['permit'] = now_user.groupid == 1 or box.user == now_user.name
            queue.append(q)
        return render_template('boxqueue.html',
                               queue=queue,
                               create_images=[i['name'] for i in getImages()])

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
    elif Box.query.filter_by(user=now_user.name, box_name=image).first():
        parent = Box.query.filter_by(user=now_user.name, box_name=image).first()
        image = parent.getBackupname()
        parent.commit(check=False)
        boxPush(parent.id)
    else:
        abort(403, 'No such environment')

    if len(BoxQueue.query.filter_by(user=now_user.name).all()) > 10:
        abort(403, 'You have more than 10 in queue')

    boxqueue = BoxQueue(user=now_user.name,
                        image=image,
                        command=data['command'])
    db.session.add(boxqueue)
    db.session.commit()
    return redirect(url_for('labboxmain.box_models.queue'))


def getBoxQueue():
    now_user = flask_login.current_user
    data = request.form
    if data.get('name', '').count('-') != 1:
        abort(403, 'Wrong Name')
    if now_user.groupid != 1:
        box = BoxQueue.query.filter_by(user=now_user.name,
                                       id=int(data.get('name').split('-')[1])).first()
    else:
        box = BoxQueue.query.filter_by(id=int(data.get('name').split('-')[1])).first()
    if not box:
        abort(403, 'Not your command')
    return box


@bp.route('/log', methods=['POST'])
@flask_login.login_required
# TODO make more pretty
def log():
    box = getBoxQueue()
    logger.debug('[Queue] ' + ' log ' + box.getName())
    if box.queueing:
        abort(403, 'Not yet creating')
    return jsonify(box.getLog())


@bp.route('/queueDelete', methods=['POST'])
@flask_login.login_required
def queueDelete():
    box = getBoxQueue()
    now_user = flask_login.current_user
    logger.debug('[Queue] ' + now_user.name + ' delete ' + box.getName())
    otherAPI('delete', name=box.getName(), check=False)
    db.session.delete(box)
    db.session.commit()
    return redirect(url_for('labboxmain.box_models.queue'))


def decisionFunc(value):
    duty = sum(value[0]) / len(value[0])
    memory = sum(value[1]) / len(value[1])
    return duty < 10 and memory < 1


def getGPUStatus():
    gpu_st = {}
    for query_metric in bp.gpu_query_metrics:
        params = {
            'query': query_metric,
            'start': str(time.time() - bp.gpu_query_interval),
            'end': str(time.time()),
            'step': 5
        }
        rep = requests.get(bp.gpu_url + 'query_range', params=params).json()
        metrics = rep['data']['result']

        for met in metrics:
            id = (met['metric']['node_name'], met['metric']['minor_number'])
            value = [float(i[1]) for i in met['values']]
            gpu_st[id] = gpu_st.get(id, []) + [value]
    return gpu_st


def getAvailableGPUs():
    gpu_st = getGPUStatus()
    avail_gpu = []
    for gpu in gpu_st.items():
        a = bp.r_cli.get(str(gpu[0]))
        if not a or time.time() - float(a) > bp.gpu_exe_interval \
                and decisionFunc(gpu[1]):
            avail_gpu.append(gpu[0])
    return avail_gpu


@celery.task()
def scheduleGPU():
    avail_gpus = getAvailableGPUs()
    boxqueue = BoxQueue.query.filter_by(queueing=True).limit(len(avail_gpus)).all()
    for i, box in enumerate(boxqueue):
        logger.debug('[Queue] ' + box.getName() + ' use ' + str(avail_gpus[i]))
        box.run(avail_gpus[i])
