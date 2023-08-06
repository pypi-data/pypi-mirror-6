#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys

import schevo
import schevo.gtk2
import schevo.gtk2.application as _app

__all__ = ['browse_db_by_name']

def browse_db_by_name(db_alias, handlerClass=_app.Application):
    widget = handlerClass()
    print "Working on database=%r" % db_alias
    
    try:
        with widget.database_open(db_alias) as db:
            print db
    except Exception: 
        raise
    else:
        widget.run()

if __name__ == '__main__':
    if len(sys.argv) >= 1:
        browse_db_by_name(sys.argv[1])
    else:
        print("Usage: schevo-editor.py <dbname>")
        sys.exit(2)

