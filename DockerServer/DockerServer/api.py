from flask import Flask, request, jsonify, abort
import docker

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
    return jsonify({'error': 'Error'})

@app.errorhandler(404)
def Error(e):
    return jsonify({'error': 'NotFound'})

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

if __name__=='__main__':
    app.run()
