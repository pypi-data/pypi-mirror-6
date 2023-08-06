Template Processing with Mako
==============================

:Last modified: 2010-07-12
:Author: Etienne Robillard <erob@gthcfoundation.org>
:Version: 0.4.1

This is a short introduction to Unicode templates processing 
in notmm. 

Unicode Templates Processing
-----------------------------

A Unicode-aware backend is provided in the 
``notmm.utils.template.makoengine`` package. 

In short, its a simple wrapper around the Mako 
template library supporting full Unicode (UTF-8) support and caching control.

Configuration
--------------

To configure and use within a WSGI or Django app:

1. Install the ``wsgiapp`` app::

    % cd notmm-0.4.1/contrib
    % sudo python setup.py develop --prefix=/usr/local

2. Add the following code to your ``development.ini`` file ::

    [wsgiapp]
    template_loader = notmm.utils.template.makoengine.TemplateLoader

3. Add the following lines to sitecustomize.py ::

    import sys
    sys.setdefaultencoding('utf-8')

4. Put the sitecustomize.py script somewhere in your ``PYTHONPATH``.

TODO
-----

* Add missing docstrings for the notmm.utils.template package (TemplateLoaderFactory)
* Add a generic way to create custom template loaders instances in ``notmm.templates.generic``
* Write more testcases 

Further readings
-----------------

* `Mako Templates for Python <http://www.makotemplates.org/>`_
* `Introduction to ConfigObj <http://www.voidspace.org.uk/python/articles/configobj.shtml/>`_

