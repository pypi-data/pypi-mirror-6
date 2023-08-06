#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2007-2012 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# <LICENSE=ISC>
# XXX: deprecated don't use unless you know what you're doing. :-)
"""Django configuration settings for the BlogEngine app.

Usage: To use in a typical Django project, add the following line in your 
local_settings.py file:
::

    from blogengine.config.settings import *

Settings overview
-----------------

TODO

"""
from django.conf.global_settings import *
BLOGENGINE_ENABLE_I18N = False
BLOGENGINE_DEBUG = DEBUG
BLOGENGINE_ITEMS_PER_PAGE = 8
BLOGENGINE_PAGE_MAX = 1

USE_I18N = BLOGENGINE_ENABLE_I18N
ADDTHIS_USERNAME = 'erob'
