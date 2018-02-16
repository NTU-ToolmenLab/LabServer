from flask import Flask, redirect, url_for, request, render_template
import ContainerServer
import json

app = Flask(__name__)
nowUser = ContainerServer.User("name")

@app.route('/')
def Login():
    return render_template('Login.html')

@app.route('/lists')
def lists():
    lists = nowUser.list()
    return render_template('lists.html', container_list = lists)


@app.route('/apis', methods=['POST'])
def apis():
    data = request.get_json()
    if data['method'] == 'Resume':
        nowUser.resume(data['id'])
    elif data['method'] == 'Restart':
        nowUser.restart(data['id'])
    elif data['method'] == 'Reset':
        nowUser.reset(data['id'])
    elif data['method'] == 'Remove':
        nowUser.remove(data['id'])
    else:
        print("Error")
        pass # unknown
    return lists()

if __name__=='__main__':
    # app.run()
    app.run(debug = True)
