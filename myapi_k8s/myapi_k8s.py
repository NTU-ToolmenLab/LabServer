from kubernetes import client, config
from flask import Flask, jsonify, redirect, request, abort
import yaml


config.load_incluster_config()
v1 = client.CoreV1Api()
app = Flask(__name__)
ns = 'default'
label = 'UserDocker'


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found'
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp


@app.errorhandler(500)
def internal_eroor(error=None):
    message = {
        'status': 500,
        'message': 'Internal Error'
    }
    resp = jsonify(message)
    resp.status_code = 500
    return resp

def ok():
    return jsonify({
        'status': 200,
        'message': 'ok'
    })

def listDockerServer():
    pods = v1.list_pod_for_all_namespaces(watch=False)
    dockerserver = []
    for pod in list(pods.items):
        if pod.spec.containers[0].name == 'dockerserver':
            dockerserver.append(pod)
    pods = [{ 'name': pod.spec.node_name,
              'ip': pod.status.pod_ip } for pod in dockerserver]
    return pods


def checkLabel(name):
    try:
        rep = v1.read_namespaced_pod(request.form.get('name'), ns)
        if not rep.metadata.labels[label]:
            abort(404)
    except:
        abort(404)
    return rep


def checkNode(node):
    for pod in listDockerServer():
        if pod['name'] == node:
            return True
    abort(404)


def parsePod(pod):
    return {
        'name': pod.metadata.name,
        'image': pod.spec.containers[0].image,
        'status': pod.status.phase,
        'reason': pod.status.reason,
        'start': pod.status.start_time,
        'id': pod.status.container_statuses[0].container_id,
        'ip': pod.status.pod_ip,
        'node': pod.spec.node_name,
    }


@app.route('/listnode')
def getDockerServer():
    return jsonify(listDockerServer())


@app.route('/<node>/<path:subpath>', methods=['POST'])
def goRedir(node, subpath):
    app.logger.info(node)
    app.logger.info(subpath)
    for pod in listDockerServer():
        if pod['name'] == node:
            return redirect('http://' + pod['ip'] + ':3476/' +  subpath, code=307)
    return not_found()


# args: name, (image, node, labnas=True, homenas=True, homepath)
@app.route('/create', methods=['POST'])
def create():
    template = yaml.load(open('/app/template.yml'))
    template['metadata']['name'] = request.form['name']
    app.logger.info("Create " + request.form['name'])
    if request.form.get('image'):
        template['spec']['containers'][0]['image'] = request.form.get('image')
    if request.form.get('node') and checkNode(request.form.get('node')):
        template['spec']['nodeSelector']['kubernetes.io/hostname'] = request.form.get('node')

    # deal with volume
    noclaim = []
    if not request.form.get('labnas', 'True').lower() == 'true':
        noclaim.append('labnas')
    if not request.form.get('homenas', 'True').lower() == 'true':
        noclaim.append('homenas')
    for vol in template['spec']['volumes']:
        if vol['name'] in noclaim:
            del vol['persistentVolumeClaim']

    for vol in template['spec']['containers'][0]['volumeMounts']:
        if vol['name'] == 'homenas' and request.form.get('homepath'):
            vol['subPath'] = request.form.get('homepath')

    rep = v1.create_namespaced_pod(ns, template)
    return ok()


@app.route('/delete', methods=['POST'])
def delete():
    name = request.form['name']
    checkLabel(name)
    app.logger.info("Delete " + request.form['name'])
    rep = v1.delete_namespaced_pod(name, ns, client.V1DeleteOptions())
    return ok()


@app.route('/listpod', methods=['POST'])
def listPod():
    if request.form.get('name'):
        rep = checkLabel(request.form.get('name'))
        pod = parsePod(rep)
    else:
        rep = v1.list_namespaced_pod(ns, label_selector=label)
        pod = [parsePod(pod) for pod in rep.items]
    return jsonify(pod)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3476) # , debug=True)
