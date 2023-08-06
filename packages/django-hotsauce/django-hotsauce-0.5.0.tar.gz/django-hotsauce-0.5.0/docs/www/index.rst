====================
notmm toolkit v0.4.5
====================

- About_
- Features_
- Examples_
- Download_
- Community_
- License_

About
=======

Intro
-----

Welcome to the notmm toolkit, a open and accessible web
publishing platform on top of Django and WSGI.

XXX more details here !

Design philosophy
-----------------

**Scalable and non-monolithic By Design**

Allow developers to write scalable Django apps easily. The notmm toolkit
provides a modular API to develop reusable WSGI applications 
environment on top of the Django framework.

.. Also backward compatible with legacy Django apps (0.96.3) and Django (1.3).

**Pragmatic Web Application Development**

Allow developers to test and develop server side WSGI applications in 
a restricted environment by writing unit tests.

**Rapid Framework Refactoring**

Based on the ``unittest`` module for continuous integration and
rapid web framework refactoring. 

**Open Source**

Fully open source licensed (ISC). The notmm toolkit works best
under the Linux OS or a BSD variant. 

Features
========

- Follows the `WSGI`_ 1.0 specification for development of related HTTP-based libraries in Python.
- Supports most Django apps designed for Django, including Satchmo, FeinCMS, and more.
- MVC (``Model-View-Controller``) API design with built-in regular-expression URL dispatching.
- UTF-8 template loading, rendering, and caching. (`Mako`_, `Beaker`_ ``New``)
- Memcache backend support tools. (``New``)
- The `API pages`_ and the `Developer Handbook`_ are generated with `Doxygen`_ and `Sphinx`_ respectively. 
- Compatible with Python 2.5, 2.6, and 2.7. 
- Commercial support kindly offered and available on request. :)

Experimental Features
---------------------

- Experimental ``AES`` encryption of picklable Python objects using `pycryptopp`_
- Experimental `SQLAlchemy`_ database backends and functions. (Declarative mapper, `Elixir`_)
- Experimental non-relational database backends and functions. (`Schevo`_, `MongoDB`_)
- Experimental ``unittest2`` integration in the ``notmm.utils.test`` package. 
- Experimental ``I18N`` support. (Based on Django's I18N framework) 
- Experimental ``C bindings`` generation with `Cython`_. 

Examples
========

Please see the `wiki`_ for real-world examples of applications using the notmm
toolkit. In addition, the ``examples`` directory should includes demo apps to 
experiment freely.

.. _wiki: https://gthc.org/wiki/NotAMonolithicMashup/Examples

Download
========

Current stable release is ``0.4.4``. 

Development
-----------

Mercurial is the current SCM used for development.

For read-only access to the source code repository: 

    hg clone http://bitbucket.org/erob/notmm/ notmm-0.4-current

Releases
--------

Releases are now being documented on the `Releases`_ page. 

.. _Releases: https://gthc.org/NotAMonolithicMashup/Releases

PGP signatures
--------------

Please use the key ID ``0xA086DDEC`` to verify the downloaded files
with your favorite GPG client.

Mirrors
-------

- `Master site <http://gthc.org/distfiles/notmm/>`_
- `PyPI archive site (Cheeseshop) <http://pypi.python.org/pypi/notmm/>`_

Let me know if you're interested in mirroring notmm source code on a public
HTTP or FTP server at erob@gthcfoundation.org. :)

Community
=========

- Wiki: https://gthc.org/wiki/NotAMonolithicMashup/
- Bug tracker: http://saya.gthc.org/bugzilla/
- Forum: http://notmm-discuss.981028.n3.nabble.com/

You can put the following logo on your website if you want to support 
the notmm toolkit:

.. image:: http://gthc.org/media/img/powered-by-notmm.png
  :alt: This website is powered by notmm! 

Related projects
----------------

Related or alternative projects you might be interested to dive in:

**Apache webserver**

- `Apache/mod_perl <http://perl.apache.org/>`_
- `Apache/mod_python <http://www.modpython.org/>`_

**Python web application frameworks**

- `Django`_
- `Pylons <http://www.pylonshq.com/>`_
- `TurboGears <http://turbogears.org/>`_
- `Twisted <http://twistedmatrix.com/trac/>`_
- `Werkzeug <http://werkzeug.pocoo.org/>`_

**Futher readings**

- `Python web frameworks <http://wiki.python.org/moin/WebFrameworks>`_
- `Framework wiki page on wsgi.org <http://www.wsgi.org/wsgi/Frameworks>`_
- `Python web application frameworks page on wikipedia.org <http://en.wikipedia.org/wiki/Category:Python_web_application_frameworks>`_
- `PEP-333 (WSGI) <http://www.python.org/dev/peps/pep-0333/>`_

Outro
-----

Do not hire a man who does your work for money, but him who does it for love of it. -- Henry David Thoreau

.. image:: https://gthc.org/media/img/turtle.gif

License
=======

Copyright (c) 2007-2011 Etienne Robillard <erob@gthcfoundation.org>

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

.. _WSGI: http://www.python.org/dev/peps/pep-0333/
.. _FastCGI: http://www.fastcgi.com/
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _Mako: http://www.makotemplates.org/
.. _Doxygen: http://www.stack.nl/~dimitri/doxygen/ 
.. _Elixir: http://elixir.ematia.de/trac/wiki/
.. _API pages: http://gthc.org/projects/notmm/refapi/
.. _Beaker: http://beaker.groovie.org/
.. _pycryptopp: http://allmydata.org/trac/pycryptopp/
.. _pickle: http://docs.python.org/library/pickle.html
.. _YAML: http://www.yaml.org/ 
.. _Schevo: http://www.schevo.org/
.. _MongoDB: http://www.mongodb.org/
.. _Cython: http://www.cython.org/
.. _Python: http://www.python.org/
.. _Django: http://www.djangoproject.org/
.. _DjangoBugfixes: https://gthc.org/wiki/DjangoBugfixes
.. _Sphinx: http://sphinx.pocoo.org/
.. _Developer Handbook: https://gthc.org/documentation/notmm/handbook/

