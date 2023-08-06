#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2007-2012 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.

# For documentation and usage see
# http://gthc.org/NotAMonolithicMashup/I18NController

from .wsgi import WSGIController

__all__ = ['I18NController']


class I18NController(WSGIController):

    charset = 'en'

    def __init__(self, *args, **kwargs):
        super(I18NController, self).__init__(*args, **kwargs)
        
        self.init_request(self.environ)


    def init_request(self, environ):
        # put the user defined charset into the wsgi request environment
        if not 'wsgi.i18n.charset' in environ:
            environ['wsgi.i18n.charset'] = self.charset

        super(I18NController, self).init_request(environ)
