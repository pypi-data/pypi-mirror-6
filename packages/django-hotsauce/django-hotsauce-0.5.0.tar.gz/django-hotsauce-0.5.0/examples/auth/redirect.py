#!/usr/bin/env python
#from authkit.authenticate import middleware
from notmm.controllers.wsgi import WSGIController
from notmm.controllers.auth import LoginController
from notmm.utils.http import httpserver
from notmm.utils.configparse import loadconf
#from notmm.utils.django_settings import LazySettings
sample_app = WSGIController()
settings = sample_app.settings
global_conf = loadconf('auth.conf')
auth_conf = global_conf['authkit']
#import pdb; pdb.set_trace()
auth_app = LoginController(sample_app, auth_conf, settings=settings)
if __name__ == '__main__':
    httpserver.daemonize(auth_app, ('localhost', 8000))
