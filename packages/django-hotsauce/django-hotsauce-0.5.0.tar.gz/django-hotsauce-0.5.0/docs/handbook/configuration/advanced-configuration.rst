Configuration
==============

:Last modified: 2010-07-12
:Author: Etienne Robillard <erob@gthcfoundation.org>
:Version: 0.4.1

Some quick notes on configuration for emerging-like web apps. 

Basic controller configuration is now done using a 'development.ini'
file located at the root of the project directory. In essence, this
configuration file is just a plain text file with config options. The
format of this file is mostly ``RFC-822`` like ::

    [myapp.blogs] 
    
    # specify default SQLite3 schema here
    schema=sqlite:////var/db/blogs.db

In addition, a quite modern web app can selectively load Django settings
using a Python module. This is also maintained for backward-compatibility
with Django. ::

    % export DJANGO_SETTINGS_MODULE=myapp.settings
    % edit development.ini 
    % ... hack hack hack ...
    % bin/debug.sh runserver localhost:8000 

Also, for consistency, new settings should be defined in the development.ini
file instead of trying to reuse original Django settings. This strategy
provides flexible configuration for WSGI applications requiring the use of
additional configuration options at runtime.

Care should also be used for not overlapping Django settings with similar
variables names. Likewise, its generally better to use ``TEMPLATE_DIRS``
than redefining another ``template_dirs`` options.

Examples
--------

setup_all
+++++++++

Here's an example of a simple app (named ``myapp``) configuration using the ``setup_all``
hook ::

    from notmm.utils.configparse import setup_all
    global_conf = {'debug' : True}
    setup_all(__name__, global_conf)

Then, later in a view, you can access the ``global_conf`` dict instance by
using a simple import statement ::

    from myapp import global_conf
    print global_conf
    {'myapp' : {'debug' : True}}

