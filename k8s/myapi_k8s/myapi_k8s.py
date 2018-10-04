from kubernetes import client, config
from flask import Flask, jsonify, redirect, request

config.load_incluster_config()
v1 = client.CoreV1Api()
app = Flask(__name__)

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

def listDockerServer():
    pods = v1.list_pod_for_all_namespaces(watch=False)
    dockerserver = []
    for pod in list(pods.items):
        if pod.spec.containers[0].name == 'dockerserver':
            dockerserver.append(pod)
    pods = [{ 'name': pod.spec.node_name,
              'ip': pod.status.pod_ip } for pod in dockerserver]
    return pods

@app.route("/list")
def getDockerServer():
    return jsonify(listDockerServer())

@app.route('/<server>/<path:subpath>', methods=['POST'])
def goRedir(server, subpath):
    app.logger.info(server)
    app.logger.info(subpath)
    for pod in listDockerServer():
        if pod['name'] == server:
            return redirect('http://' + pod['ip'] + ':3476/' +  subpath, code=307)
    return not_found()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3476) # , debug=True)
