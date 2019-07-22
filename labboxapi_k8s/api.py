from kubernetes import client, config
from flask import Flask, jsonify, redirect, request, abort
import yaml
import re


config.load_incluster_config()
v1 = client.CoreV1Api()
v1beta = client.ExtensionsV1beta1Api()

app = Flask(__name__)
ns = 'user'
label = 'UserDocker'


@app.errorhandler(403)
def forbidden(error=None):
    message = {
        'status': 403,
        'message': error or 'Fail'
    }
    resp = jsonify(message)
    resp.status_code = 403
    return resp


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
def internal_error(error=None):
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
        if pod.spec.containers[0].name == 'labboxapi-docker':
            dockerserver.append(pod)
    pods = [{'name': pod.spec.node_name,
             'ip': pod.status.pod_ip} for pod in dockerserver]
    return pods


def checkLabel(name):
    try:
        rep = v1.read_namespaced_pod(name, ns)
        if not rep.metadata.labels[label]:
            abort(404)
    except client.rest.ApiException:
        abort(404)
    return rep


def checkNode(node):
    for pod in listDockerServer():
        if pod['name'] == node:
            return True
    abort(404)


def parsePod(pod):
    dockerid = ''
    # container_id has prefix docker://
    if pod.status.container_statuses[0].container_id:
        dockerid = re.findall(r'\w+$', pod.status.container_statuses[0].container_id)[0]
    return {
        'name': pod.metadata.name,
        'image': pod.spec.containers[0].image,
        'status': pod.status.phase,
        'reason': pod.status.reason,
        'start': pod.status.start_time,
        'id': dockerid,
        'ip': pod.status.pod_ip,
        'node': pod.spec.node_name,
    }


@app.route('/listnode', methods=['POST'])
def getDockerServer():
    return jsonify(listDockerServer())


@app.route('/<node>/<path:subpath>', methods=['POST'])
def goRedir(node, subpath):
    app.logger.info(node)
    app.logger.info(subpath)
    for pod in listDockerServer():
        if pod['name'] == node:
            return redirect('http://' + pod['ip'] + ':3476/' + subpath, code=307)
    return not_found()


# args: name, (image, node, homepath, labnas=True, inittar=server/ServerBox/all.tar, pull=True)
@app.route('/create', methods=['POST'])
def create():
    template = yaml.load(open('/app/pod.yml'))
    name = request.form['name']
    template['metadata']['name'] = name
    template['metadata']['labels']['srvname'] = name
    template['metadata']['namespace'] = ns
    app.logger.info("Create " + name)

    if request.form.get('image'):
        template['spec']['containers'][0]['image'] = request.form.get('image')
    if request.form.get('node') and checkNode(request.form.get('node')):
        template['spec']['nodeSelector']['kubernetes.io/hostname'] = request.form.get('node')

    # deal with volume
    noclaim = []
    if not request.form.get('labnas', 'True').lower() == 'true':
        noclaim.append('labnas')
    if not request.form.get('homepath'):
        noclaim.append('homenas')
    for vol in template['spec']['volumes']:
        if vol['name'] in noclaim:
            del vol['persistentVolumeClaim']

    for vol in template['spec']['containers'][0]['volumeMounts']:
        if vol['name'] == 'homenas' and vol['subPath'] == 'guest' and request.form.get('homepath'):
            vol['subPath'] = request.form.get('homepath')
    for vol in template['spec']['initContainers'][0]['volumeMounts']:
        if not vol.get('readOnly') and request.form.get('homepath'):
            vol['subPath'] = request.form.get('homepath')
        if not vol.get('readOnly') and request.form.get('inittar'):
            vol['subPath'] = request.form.get('inittar')

    # pull
    if request.form.get('pull'):
        template['spec']['containers']['imagePullPolicy'] = "Always"

    # create pod
    try:
        rep = v1.read_namespaced_pod(name, ns)
        return forbidden('Double Creation')
    except client.rest.ApiException:
        v1.create_namespaced_pod(ns, template)

    # ingress
    template_ingress = yaml.load(open('/app/pod_ingress.yml'))
    template_ingress['metadata']['name'] = name
    path = template_ingress['spec']['rules'][0]['http']['paths'][0]
    path['path'] = path['path'].replace('hostname', name)
    path['backend']['serviceName'] = name

    # service
    template_service = yaml.load(open('/app/pod_service.yml'))
    template_service['metadata']['name'] = name
    template_service['spec']['selector']['srvname'] = name

    # create
    try:
        v1.create_namespaced_service(ns, template_service)
    except client.rest.ApiException:
        pass
    try:
        v1beta.create_namespaced_ingress(ns, template_ingress)
    except client.rest.ApiException:
        pass

    return ok()


@app.route('/delete', methods=['POST'])
def delete():
    name = request.form.get('name')
    checkLabel(name)
    app.logger.info("Delete " + request.form['name'])
    # using exception bcz didn't check
    try:
        v1.delete_namespaced_pod(name, ns)
    except client.rest.ApiException:
        pass
    try:
        v1.delete_namespaced_service(name, ns)
    except client.rest.ApiException:
        pass
    try:
        v1beta.delete_namespaced_ingress(name, ns)
    except client.rest.ApiException:
        pass
    return ok()


@app.route('/search', methods=['POST'])
def listPod():
    if request.form.get('name'):
        rep = checkLabel(request.form.get('name'))
        pod = parsePod(rep)
    else:
        rep = v1.list_namespaced_pod(ns, label_selector=label)
        pod = [parsePod(pod) for pod in rep.items]
    return jsonify(pod)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3476)  # , debug=True)
