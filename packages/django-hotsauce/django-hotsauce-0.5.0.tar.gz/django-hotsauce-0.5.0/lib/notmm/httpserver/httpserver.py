#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2007-2012 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# <LICENSE=ISC> 
"""HTTP server utilities based on the ``wsgiref`` module.

"""

import sys, urllib
from wsgiref import simple_server, validate
from notmm.utils.configparse import string_getter, int_getter

__all__ = ('HTTPServer',
           'get_bind_addr', 
           'daemonize', 
           'make_server')

class HTTPServer(object):
    """Wrapper class to configure a simple HTTP server instance"""
    
    # Uncomment this to enable cherrypy based http daemon
    # serverClass = wsgiserver.CherryPyWSGIServer
    
    serverClass = simple_server # wsgiref
    
    def __init__(self, wsgi_app, bind_addr, debug=False):
        """HTTPServer.__init__"""
        self.host = bind_addr[0]
        self.port = bind_addr[1]
        if debug:
            # run the wsgi app in using wsgiref validator
            # middleware
            self.request_handler = validate.validator(wsgi_app)
        else:
            self.request_handler = wsgi_app

        self.server = self.serverClass.make_server(self.host, self.port, self.request_handler)
    
    def serve(self):
        self.server.serve_forever()

def get_bind_addr(app_conf, section='httpserver', listen_port=8000):
    """
    Return a 2-element tuple containing the hostname and port
    to listen for remote connections.
    """

    host = string_getter(app_conf, section, 'host') or urllib.localhost()
    port = int_getter(app_conf, section, 'port') or listen_port

    return (host, port)

def daemonize(wsgi_app, bind_addr, logging=False, autoreload=True):
    """
    Create an instance of a validating WSGI server for 
    development purposes.
    
    """
    

    # Install translogger middleware if logging is enabled
    if logging:
        from paste.translogger import TransLogger
        request_handler = TransLogger(wsgi_app)
    else:
        request_handler = wsgi_app
    
    # Add optional autoreloading support (see the docstring for help
    # on installing this)
    if autoreload:
        try:
            import paste.reloader as reloader
            reloader.install()
        except ImportError:
            pass
    server = HTTPServer(request_handler, bind_addr)

    try:
        server.serve()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)

