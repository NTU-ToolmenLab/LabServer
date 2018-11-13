from flask import Flask, request, jsonify, abort
import docker
import ast

app = Flask(__name__)
app.secret_key = 'super secret string1'  # Change this!

def getContainer(query):
    client = docker.from_env().containers
    try:
        container = client.get(query)
        return container
    except docker.errors.NotFound:
        abort(404)

@app.errorhandler(500)
def Error(e):
    return jsonify({'error': str(e)})

@app.errorhandler(404)
def Error(e):
    return jsonify({'error': str(e)})

def Ok():
    return jsonify({'ok': 'true'})

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('name')
    container = getContainer(query)
        
    return jsonify({
        'id': container.id,
        'name': container.name,
        'status': container.status,
        'ip': list(container.attrs['NetworkSettings']['Networks'].items())[0][1]['IPAddress']
    })

@app.route('/start', methods=['POST'])
def start():
    name = request.form.get('name')
    container = getContainer(name)
    container.start()
    return Ok()

@app.route('/stop', methods=['POST'])
def stop():
    name = request.form.get('name')
    container = getContainer(name)
    container.stop()
    return Ok()

@app.route('/restart', methods=['POST'])
def restart():
    name = request.form.get('name')
    container = getContainer(name)
    container.restart()
    return Ok()

@app.route('/passwd', methods=['POST'])
def passwd():
    name = request.form.get('name')
    container = getContainer(name)
    if not container.attrs['State']['Running']:
        abort(404)
    pw = request.form.get('pw')
    pwd = pw.replace(r'/', r'\/').replace('$',r'\$')
    # Is it not robost ?
    rest = container.exec_run(r'perl -p -i -e "s/(ubuntu:).*?(:.+)/\1' + pwd + r'\2/g" /etc/shadow')
    return Ok()

@app.route('/commit', methods=['POST'])
def commit():
    name = request.form.get('name')
    newname = request.form.get('newname', name)
    container = getContainer(name)
    container.commit(newname)
    return Ok()

@app.route('/push', methods=['POST'])
def push():
    client = docker.from_env()
    name = request.form.get('name')
    try:
        client.images.get(name)
    except docker.errors.ImageNotFound:
        return Error("Not Find Image")

    username = request.form.get('username')
    password = request.form.get('password')
    registry = request.form.get('registry')

    client.login(username, password=password, registry=registry)
    rep = client.images.push(name)
    for r in rep.split('\n'):
        if r and ast.literal_eval(r).get('error'):
            return jsonify({'error': ast.literal_eval(r).get('error')})
    client.images.remove(name)
    return Ok()

if __name__=='__main__':
    app.run()
