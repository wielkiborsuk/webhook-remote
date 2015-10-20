import subprocess
import os
import json
from flask import Flask
from flask import render_template
app = Flask(__name__)

cmus_path = os.path.expanduser('~/.cmus')


@app.route("/")
def hello():
    return render_template('index.html')
    # return "Welcome to remote, here are available hooks"


@app.route("/cmus")
def cmus_status():
    # TODO - process the status to take out trash
    status = subprocess.check_output(['cmus-remote', '-Q']).decode()
    return status


@app.route('/cmus/play')
def cmus_play():
    subprocess.call(['cmus-remote', '-u'])
    return 'OK'


@app.route('/cmus/stop')
def cmus_stop():
    subprocess.call(['cmus-remote', '-s'])
    return 'OK'


@app.route('/cmus/list')
def cmus_lists():
    lst = subprocess.check_output(['ls', cmus_path]).decode().split()
    lst = [x for x in lst if x.endswith('.pls')]

    return json.dumps(lst, ensure_ascii=False)


def find_list(list):
    args = [list, list+'.pls']
    for f in args:
        file_path = os.path.join(cmus_path, f)
        if os.path.exists(file_path):
            return file_path

    return None


@app.route('/cmus/list/<list>')
def cmus_list_select(list):
    path = find_list(list)
    if path:
        subprocess.call(['cmus-remote', '-c', path])
        subprocess.call(['cmus-remote', '-n'])
        return 'OK'

    return 'No such list'


# @app.route('/cmus/mute')
# def cmus_mute():
    # subprocess.call(['cmus-remote', ''])
    # return 'OK'


if __name__ == "__main__":
    app.debug = True
    app.run('0.0.0.0')
