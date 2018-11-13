from flask import Flask, request, jsonify, abort
import docker
import ast

app = Flask(__name__)
app.secret_key = 'super secret string1'  # Change this!
label = 'UserDocker'
default_homepath = '/nashome/'
default_naspath = '/home/nas/'
client = docker.from_env()


@app.errorhandler(500)
def Error(e):
    message = {
        'status': 500,
        'message': 'Internal Error'
    }
    resp = jsonify(message)
    resp.status_code = 500
    return resp


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': str(error) or 'Not Found'
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp


def Ok():
    return jsonify({
        'status': 200,
        'message': 'ok'
    })


def getContainer(query, one=True):
    try:
        container = client.containers.get(query)
        if label not in container.labels:
            abort(404)
        return container
    except docker.errors.NotFound:
        abort(404)


def parseContainer(cont):
    return {
        'name': cont.name,
        'image': cont.attrs['Config']['Image'],
        'status': cont.status,
        'reason': cont.status,
        'start': cont.attrs['Created'],
        'id': cont.id,
        'ip': cont.attrs['NetworkSettings']['IPAddress']
    }


@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('name')
    output = []
    if not query:
        allcontainer = client.containers.list(filters={'label': label})
        output = [parseContainer(c) for c in allcontainer]
    else:
        container = getContainer(query)
        output = parseContainer(container)

    return jsonify(output)


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
    pwd = pw.replace(r'/', r'\/').replace('$', r'\$')
    # Is it not robost ?
    rest = container.exec_run(
        r'perl -p -i -e "s/(ubuntu:).*?(:.+)/\1' + pwd + r'\2/g" /etc/shadow')
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
    name = request.form.get('name')
    try:
        client.images.get(name)
    except docker.errors.ImageNotFound:
        return Error('Not Find Image')

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


@app.route('/create', methods=['POST'])
def create():
    image = request.form.get('image')
    try:
        client.images.get(image)
    except docker.errors.ImageNotFound:
        return Error('Not Find Image')

    name = request.form.get('name')
    homenas = request.form.get('homenas', 'False').lower() == 'true'
    homepath = request.form.get('homepath')
    labnas = request.form.get('labnas', 'False').lower() == 'true'
    if not name or (homenas and not homepath):
        return Error('no home dictionary')

    mounts = []
    if homenas:
        mounts.append(docker.types.Mount('/home/ubuntu',
                      default_homepath + homepath, type='bind'))
    if labnas:
        mounts.append(docker.types.Mount('/home/nas',
                      default_naspath, type='bind'))

    cont = client.containers.run(image,
                                 name=name,
                                 mounts=mounts,
                                 command='tail -f /dev/null',  # test
                                 labels={label: 'True'},
                                 detach=True,
                                 restart_policy={'Name': 'always'})
    return Ok()


@app.route('/delete', methods=['POST'])
def delete():
    name = request.form.get('name')
    container = getContainer(name)
    container.stop()
    container.remove()
    return Ok()


if __name__ == '__main__':
    app.run()
