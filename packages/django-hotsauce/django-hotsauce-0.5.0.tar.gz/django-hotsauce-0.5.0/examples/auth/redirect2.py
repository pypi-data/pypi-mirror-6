#!/usr/bin/env python
from authkit.authenticate import middleware
from notmm.utils.http import httpserver
from notmm.controllers.wsgi import WSGIController

sample_app = WSGIController()

app = middleware(
    sample_app,
    setup_method=['redirect','form','cookie'],
    redirect_url='http://localhost',
    cookie_secret='asdasd'
)
if __name__ == '__main__':
    httpserver.daemonize(app, ('localhost', 8000))
