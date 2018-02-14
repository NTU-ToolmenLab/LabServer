from flask import Flask, redirect, url_for, request, render_template
import time

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/lists')
def lists():
    lists = [{"id":"id0", "name":"name0", "time": time.strftime("%c"), "url":"http://google.com"},
             {"id":"id1", "name":"name1", "time": time.strftime("%c"), "url":"http://github.com"}]
    return render_template('lists.html', container_list = lists)

if __name__=='__main__':
    app.run()
    app.run(debug = True)
