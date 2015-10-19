#!/usr/bin/env python3
import sys

sys.path.insert(0, '/home/borsuk/workspace/webhook-remote')

activate_this = '/home/borsuk/workspace/webhook-remote/local/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from remote import app as application
