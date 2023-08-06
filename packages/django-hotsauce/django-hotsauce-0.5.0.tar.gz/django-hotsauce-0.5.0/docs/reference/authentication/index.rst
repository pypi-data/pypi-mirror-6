Authentication
===============

:Last modified: 2011-02-15
:Author: Etienne Robillard <erob@gthcfoundation.org>
:Version: 0.4.3

:Keywords: AuthKit, Django

Roadmap
=======

In addition to native `SQLAlchemy <http://www.sqlalchemy.org>`_ support, active development is in progress to
develop a fully functional **Authentication and Authorization API** pluggable with 
non-sql databases like Schevo (Durus), `MongoDB <http://www.mongodb.org>`_, and `Apache Cassandra <http://cassandra.apache.org/>`_.

Implementation
==============

The following components are provided as proof-of-concept to implement a generic
cookie-based, non-blocking, authentication app using Schevo and the ``Xdserver`` 
backend. 

Core modules provided by the ``notmm.controllers`` package:

* ``auth`` - Provides the LoginController middleware, to implement custom cookie-based authentication middlewares with AuthKit.
* ``session`` - Provides the SessionController middleware with thread-local storage access to the current ``request`` object.

New extensions implemented in AuthKit: 

* ``authkit.users.schevo_04_driver``: Authentication and authorization backend for Schevo-based databases.
* ``authkit.authorize.django_adapters2``: WSGI adaptors version 2 for integrating AuthKit with Django.

Authentication middleware
-------------------------

In a stand-alone application, it is intended that the provided ``authenticate`` method 
may be used for implementing a custom authentication middleware.  

Thus, the class ``notmm.controllers.auth.LoginController`` can be configured in such ways
to handle request and responses to protected URIs to any Django-based app.

Consult the AuthKit documentation for additional details on the authentication
and authorization middlewares usage.

Overriding the ``authenticate`` method
++++++++++++++++++++++++++++++++++++++

The ``LoginController.authenticate`` method may be subclassed to customize
the basic authentication challenge.  ::

    class LoginController(SessionController):

        def authenticate(self, username, password):
            if username == password:
                # authentication succeeds, return the username as
                # a true value.
                return username
            else:
                return None

Custom ``UserManager`` subclassing
----------------------------------

The ``UserManager`` class used for delegating unauthorized requests 
to a Schevo-based User model (extent) is given below. Note that this
API is subject to changes and is relatively new.  

    from notmm.dbapi.orm import RelationProxy
    from schevo_driver.model import db
    from authkit.users import Users

    __all__ = ['UserManager']

    class UserManager(Users):
        """
        Creates a composite proxy object for the User Entity. 

        >>> manager = UserManager(db.User)
        >>> user = manager.objects.get(username="erob")
        >>> user
        <User account: "Etienne Robillard">
        >>> user.username == "erob"
        True
        """
    
        objects = None

        # Keep this for compatibility with Pylons ;-)
        api_version = 0.4

        def __init__(self, *args, **kwargs):
            # Obtain a default query set for available
            # User entities
            self.objects = self._default_manager = RelationProxy(db.User)

        def user_exists(self, username):
            #look up the user
            user_object = self.objects.get(username=username)
            if user_object is not None:
                return True
            return False

        def user_has_password(self, username, password):
            u = self.objects.get(username=username)
            if u.f.password.compare(password):
                return True
            return False    

Authorization middleware
------------------------

The ``authkit.authorize.django_adapters2`` module provides the glue for
tying WSGI components to the Django regex-based URL dispatcher and thus for
delegating cookie-based authorization to the ``UserManager`` model.

Requirements
============

* Requires authkit 0.4.6 or later (``hg clone http://joelia.gthc.org/authkit``)
* Schevo 3.2.1 or later recommended. Using Schevo 3.1 is not supported anymore. (``hg clone http://joelia.gthc.org/schevo``)
* Durus 3.9 (http://www.mems-exchange.org/software/durus/)
* ...

Get Started
===========

First obtain AuthKit using the provided setup.py script to 
develop from the source location ::

    $ hg clone http://joelia.gthc.org/authkit authkit-0.4.6
    $ cd authkit-0.4.6
    $ sudo python setup.py develop

Examples
========

Basic Usage
-----------

Basic usage, for authentication and authorization using HTTP cookies ::

    .. coding: Python


    if __name__ == '__main__':
        # Load the user-defined development.ini file
        global_conf = loadconf('development.ini')

        # Get the authentication config
        auth_conf = global_conf.get('authkit')

        # Setup the WSGI middleware environment and initialize the LoginController
        # to handles incoming authentication requests. 
        wsgi_app = WSGIController(global_conf, ...)
        ...
        wsgi_app = LoginController(wsgi_app, auth_conf)
 
        # serve
        httpserver.serve(wsgi_app)

Sample development.ini
----------------------

This example assumed you have defined a generic configuration
file with a ``authkit`` section ::

    [authkit]
    # root directory of the database 
    dbroot = /var/db/blogengine
    # authentication/authorization database name
    dbname = 'accounts'

    # middleware setup
    authkit.setup.method = redirect, form, cookie
    authkit.setup.enable = true

    authkit.redirect.url = /session_login/
    # Use the new schevo_04_driver authentication backend :)
    authkit.form.authenticate.user.type = authkit.users.schevo_04_driver:UserManager
    authkit.cookie.secret = user_id

    # don't store the username in plain-text in the cookie. breaks
    # compatibility with mod_auth_tkt..
    # authkit.cookie.enforce = true
    # authkit.cookie.nouserincookie = true
    # authkit.cookie.params.expires = 500
    authkit.cookie.signoutpath = /session_logout/

View-based authorization using a decorator function
---------------------------------------------------

To authorize a user for a particular view, assuming that authentication
has been successful (i.e: ``valid_password`` returned a True value) ::

    # authorization
    from authkit.authorize.django_adaptors2 import authorize
    from authkit.permissions import RemoteUser, ValidAuthKitUser, UserIn

    @authorize(RemoteUser())
    def restricted(request, **kwargs):
        assert 'REMOTE_USER' in request.environ
        template_name = 'restricted.html'
        return direct_to_template(request, template_name, ...)


