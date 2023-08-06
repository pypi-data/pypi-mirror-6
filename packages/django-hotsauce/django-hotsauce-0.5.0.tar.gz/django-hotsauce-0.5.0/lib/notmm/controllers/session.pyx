#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SessionController API

Copyright (c) 2007-2011 Etienne Robillard
All rights reserved.

<LICENSE=ISC>
"""
from notmm.controllers.wsgi import WSGIController

__all__ = ['SessionController']

class SessionController(WSGIController):
    """
    A simple WSGI middleware which adds a ``session`` attribute
    to the current request instance.
    """
    def __init__(self, *args, **kwargs):
        super(SessionController, self).__init__(*args, **kwargs)

    #If we define a BeakerController extension the following would
    #make sense:
    #def session_active(self, wsgi_app):
    #    return bool('beaker' in wsgi_app.environ.keys() == True)

    def process_request(self, request):
        # TODO:
        # Verify if session exists and can be
        # recuperated from persistent storage
        # if not self.request.session_active():
        #   no session data record for this IP found
        # else:
        #   retrieve the current session data
        #   Session = self.request.get_session(...)

        super(SessionController, self).process_request(request)

        # consistency checks
        #if __debug__ and self.settings.DEBUG_SESSION:
        #    assert self.request.session != None, 'Session instance must not be None.'
        return None
