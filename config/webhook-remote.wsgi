#!/usr/bin/env python3
import sys

application_root = '/path/to/applcation/root'
sys.path.insert(0, application_root)

activate_this = application_root + '/local/bin/activate_this.py'
exec(open(activate_this).read(), dict(__file__=activate_this))

from remote import app as application
