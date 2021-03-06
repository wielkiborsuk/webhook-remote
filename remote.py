import subprocess
import os
import pwd
import json
import shutil
import javaobj
import datetime
import re
from flask import Flask
from flask import render_template
from flask import request
from collections import defaultdict
from urllib.request import urlretrieve
app = Flask(__name__)

try:
    import localizator

    class LocationHandler:
        wrapper = localizator.LocatorWrapper(['borsuk', 'aga'])

        @app.route('/locations')
        def check_locations():
            return json.dumps(LocationHandler.wrapper.check_locations())

        @app.route('/where_is_borsuk')
        def location_map():
            return render_template('map.html')

except Exception as e:
    print(e)


class CmusHandler:
    cmus_path = next((x for x in ['~/.config/cmus', '~/.cmus']
                      if os.path.exists(os.path.expanduser(x))), '~')
    cmus_path = os.path.expanduser(cmus_path)

    if 'USER' not in os.environ or not os.environ['USER']:
        os.environ['USER'] = pwd.getpwuid(os.getuid()).pw_name

    if ('XDG_RUNTIME_DIR' not in os.environ
            or not os.environ['XDG_RUNTIME_DIR']):
        os.environ['XDG_RUNTIME_DIR'] = '/run/user/' + str(os.getuid())

    @app.route("/cmus")
    def cmus_status():
        status = subprocess.check_output(['cmus-remote', '-Q']).decode()
        file_name = re.search('^file [^\n]*/([^\n/]+)$', status,
                              re.MULTILINE).group(1)
        position = re.search('^position (\\d+)$', status,
                             re.MULTILINE).group(1)
        duration = re.search('^duration (\\d+)$', status,
                             re.MULTILINE).group(1)
        result = {
            'filename': file_name,
            'position': int(position)*1000,
            'duration': int(duration)*1000
        }

        return json.dumps(result)

    @app.route("/cmus/playlist")
    def cmus_playlist():
        playlist = (subprocess
                    .check_output(['cmus-remote', '-C', 'save -p -'])
                    .decode())
        playlist = [l.split('/')[-1] for l in playlist.split('\n') if l]
        return json.dumps(playlist)

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

    @app.route('/cmus/select', methods=['POST'])
    def cmus_song_select():
        file_name = request.data.decode()
        subprocess.call(['cmus-remote', '-C', '/{}'.format(file_name),
                         'win-activate'])
        return 'OK'


class AdminHandler:

    @app.route('/admin')
    def admin_dashboard():
        return render_template('admin.html')


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
        BookmarkHandler.last_file = file_name

        return file_name

    @app.route('/book_sync', methods=['POST'])
    def post_sync():
        file_uri = request.data.decode()
        file_name, headers = urlretrieve(file_uri)
        BookmarkHandler.last_file = file_name

        return file_name

    @app.route('/book_sync/last')
    def last_bookmark():
        if BookmarkHandler.last_file:
            bookmark = open(BookmarkHandler.last_file, 'rb').read()
            parsed = javaobj.loads(bookmark)

            return "{}\n{}".format(parsed.mFileName,
                                   datetime.timedelta(
                                       seconds=parsed.mFilePosition))
        return "no bookmark"


@app.route("/")
def hello():
    return render_template('index.html')


if __name__ == "__main__":
    # app.debug = True
    # app.run('0.0.0.0')
    app.run()
