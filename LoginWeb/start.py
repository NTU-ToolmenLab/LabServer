from flask import Flask, redirect, url_for, request, render_template
from Login import *
import ContainerServer
import json

app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!
login_manager.init_app(app)

nowUser = ContainerServer.User("name")

@app.route('/', methods=['GET', 'POST'])
def Login():
    if request.method == 'GET':
        return render_template('Login.html')
    else:
        user = requestParse(request)
        if not user or not user[1]:
            return redirect(url_for('Login'))
        flask_login.login_user(user[0])
        return redirect(url_for('lists'))

    return 'Bad login'

@app.route("/logout")
@flask_login.login_required
def Logout():
    flask_login.logout_user()
    return redirect(url_for('Login'))

@app.route('/lists')
@flask_login.login_required
def lists():
    lists = nowUser.list()
    return render_template('lists.html', container_list = lists)


@app.route('/apis', methods=['POST'])
@flask_login.login_required
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
    app.run()
