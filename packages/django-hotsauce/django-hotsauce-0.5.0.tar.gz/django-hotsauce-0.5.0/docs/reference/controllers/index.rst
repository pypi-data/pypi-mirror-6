BaseController API
===================

:Author: Etienne Robillard <erob@gthcfoundation.org>
:Version: 0.4.5

Introduction
-------------

The ``notmm.controllers`` package provides a simple gateway for Django apps
to extend from the ``BaseController`` class, an interface to access and 
store internal application data at runtime.

Modules
--------

``BaseController``
~~~~~~~~~~~~~~~~~~~

The ``BaseController`` module requires the ``Cython`` library to
operate properly. It purposes is to provide an abstract base class 
and a set of common methods to derived subclasses. See also
``:WSGIController:``.


``WSGIController``
~~~~~~~~~~~~~~~~~~~

The ``WSGIController`` class provides the core wrapper for Django apps
to extend from. It is essentially a thin but valid WSGI middleware to sit
between the Django and the webserver. Django 1.3 or higher is recommended 
for optimal results. 

In addition, the ``WSGIController`` supports many exclusive features
such as:

- Customized HTTP/WSGI request and response(s) handling
- Django settings autoloading via Proxy-style attribute delegation
- Allow developers to embed Django applications using a shared library..
- Makes the Pylons developers wanting to build pyramids instead of pylons.. :)

Exception Handling
-------------------

.. The following is out-of-date...

To register a custom WSGI response handler ::

    from notmm.controllers.wsgilib import WSGIController
    from myapp.config import settings as _settings_module
    
    wsgi_app = WSGIController(settings=_settings_module)
    wsgi_app.sethandle('handle404', 'myapp.views.handle404')
    wsgi_app.sethandle('handle500', 'myapp.views.handle500') 

Notes
------

* The name `BaseController' is inspired from the Pylons (Pyramid) framework.
* `Cython <http://www.cython.org/>`_ support is still experimental. 

Bugs
-----

There's probably a lots of them... ;-)

See Also
---------

The ``session`` and ``authentication`` chapters.


