import subprocess
import os
import pwd
import json
import shutil
from flask import Flask
from flask import render_template
from flask import request
from collections import defaultdict
from urllib.request import urlretrieve
app = Flask(__name__)


class CmusHandler:
    cmus_path = next((x for x in ['~/.config/cmus', '~/.cmus']
                      if os.path.exists(os.path.expanduser(x))), '~')
    cmus_path = os.path.expanduser(cmus_path)

    if 'USER' not in os.environ or not os.environ['USER']:
        os.environ['USER'] = pwd.getpwuid(os.getuid()).pw_name

    if 'XDG_RUNTIME_DIR' not in os.environ or not os.environ['XDG_RUNTIME_DIR']:
        os.environ['XDG_RUNTIME_DIR'] = '/run/user/' + str(os.getuid())

    @app.route("/cmus")
    def cmus_status():
        # TODO - process the status to take out trash
        status = subprocess.check_output(['cmus-remote', '-Q']).decode()
        playlist = (subprocess
                    .check_output(['cmus-remote', '-C', 'save -p -'])
                    .decode())
        playlist = [l.split('/')[-1] for l in playlist.split('\n')]
        return status+str(playlist)

    @app.route('/cmus/play')
    def cmus_play():
        subprocess.call(['cmus-remote', '-u'])
        return 'OK'

    @app.route('/cmus/next')
    def cmus_next():
        subprocess.call(['cmus-remote', '-n'])
        return 'OK'

    @app.route('/cmus/stop')
    def cmus_stop():
        subprocess.call(['cmus-remote', '-s'])
        return 'OK'

    @app.route('/cmus/list')
    def cmus_lists():
        lst = (subprocess.check_output(['ls', CmusHandler.cmus_path])
               .decode().split())
        lst = [x for x in lst if x.endswith('.pls')]

        return json.dumps(lst, ensure_ascii=False)

    @classmethod
    def find_list(cls, list):
        args = [list, list+'.pls']
        for f in args:
            file_path = os.path.join(cls.cmus_path, f)
            if os.path.exists(file_path):
                return file_path

        return None

    @app.route('/cmus/list/<list>')
    def cmus_list_select(list):
        path = CmusHandler.find_list(list)
        if path:
            subprocess.call(['cmus-remote', '-c', path])
            subprocess.call(['cmus-remote', '-n'])
            return 'OK'

        return 'No such list'


class WolHandler:
    macs = defaultdict(str)
    macs['nora'] = '90:2b:34:37:8a:54'
    cmd = shutil.which('wol') or shutil.which('wakeonlan')

    @app.route('/wol/<host>')
    def wol_nora(host):
        subprocess.call([WolHandler.cmd, WolHandler.macs[host]])
        return 'OK'


class BookmarkHandler:
    last_file = None

    @app.route('/book_sync/<idx>')
    def book_sync(idx):
        path = 'https://drive.google.com/uc?id={}'.format(idx)
        file_name, headers = urlretrieve(path)
        return file_name

    @app.route('/book_sync', methods=['POST'])
    def post_sync():
        file_uri = request.data.decode()
        file_name, headers = urlretrieve(file_uri)
        BookmarkHandler.last_file = file_name
        print(file_name)

        return file_name


@app.route("/")
def hello():
    return render_template('index.html')


if __name__ == "__main__":
    app.debug = True
    app.run('0.0.0.0')
