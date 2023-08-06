#!/usr/bin/env python
# Create your models here.

from notmm.dbapi.orm import XdserverProxy
#from django.conf import settings

__all__ = ['db', 'UserProxy']

db = XdserverProxy('accounts')
UserProxy = db.User

