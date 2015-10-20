#!/usr/bin/env python3
import sys
import os

application_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, application_root)

activate_this = application_root + '/local/bin/activate_this.py'
exec(open(activate_this).read(), dict(__file__=activate_this))

from remote import app as application
