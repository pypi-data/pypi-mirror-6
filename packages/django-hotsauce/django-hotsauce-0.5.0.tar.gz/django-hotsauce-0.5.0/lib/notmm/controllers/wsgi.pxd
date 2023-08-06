#!/usr/bin/env python
# Copyright (C) 2007-2012 Etienne Robillard <erob@gthcfoundation.org>
# <LICENSE=ISC>

# BaseController C API/WSGI version:    0.4.5
# Cython version:   0.15.1/0.16

#from cython import *

cdef class BaseControllerMixIn(object):
   
    #cdef object settings, resolver, request_class, response_class
    #cdef dict environ
    cdef inline application


