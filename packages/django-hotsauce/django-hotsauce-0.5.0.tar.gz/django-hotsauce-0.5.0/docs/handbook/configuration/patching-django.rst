Patching Django
================

:Last modified: 2010-07-12
:Author: Etienne Robillard <erob@gthcfoundation.org>
:Version: 0.4.1

This document attempt to explain a simple technique
for patching Django with Mercurial using the MQ extension.

Introduction
-------------

``django-bugfixes`` is a MQ repository that provides normalized patch
sets to apply on a clean Django snapshot or branch. Using the "trunk" branch 
or a official release is highly recommended, but not mandatory. 

To get the latest unofficial fixes, recommended for Django 1.3 revision 13404 or
higher:: 
    
    $ hg clone http://joelia.gthc.org/django-bugfixes/trunk/ django-bugfixes

List of available patches
--------------------------

* 002_create_default_site.patch
    A security patch for creating a default site instance without the hardcoded `example.com` value. 
* 003_request_context.patch
    This makes the ``RequestContext`` class a subclass of  the ``dict`` type.
* 004_context_processors.patch
    Minor bug fix for compatibility with ``webob``.
* 005_http404.patch
    Allow sending 404 responses with ``webob.exc.HTTPNotFound`` inside generic views.
* 006_memoize_kwargs.patch
    Allow the memoize decorator to support keyword arguments.
* 007_setup_environ.patch
    This is a experimental patch for allowing more flexible project layouts. 
* 008_template_defaultfilters.patch
    Important fix used to get ``technical_500_response`` working in a WSGI app.    
* 009_trans_real_fixes.patch
    Bugfixes for allowing the ``USE_I18N`` setting to work inside a
    ``BaseController`` app.
* 010_django_forms_has_changed.patch
    Fix forms so they return data when not implicitely implementing a ``save()``
    method or using Django models.

How to apply
-------------

First, backup your current Django tree, unless you don't care about
losing data! *:-)

Next, import the desired patch set in ``$DJANGO_HOME`` ::

    $ cd $DJANGO_HOME
    $ hg init && hg qinit -c  # init a new hg and mq repos (recommended step)
    $ hg add                  # creates a pristine copy (optional step)
    $ hg commit               # and commit..
    $ hg qpush -a             # apply all patches found in the series file

If you're lazy, here's a nifty trick to import patches from a 
specific directory into your Django tree ::

    $ cd <project_directory>
    $ ls /path/to/django.bugfixes/trunk/*.patch | xargs hg qimport 
    $ hg qpush -a 

Here I've imported patches from the "trunk" directory, but you could have used
any other directory holding a arbitrary set of patches.

Another method for manipulating patch sets visually is to use the gquilt
gui frontend: http://gquilt.sourceforge.net/

How to stay current
--------------------

If you like maintaining Django with patchs (I do), you'll find the ``hg qrefresh``
command a very useful tool.

For example, to refresh a patch which cannot be
applied cleanly, the command ::

    $ hg qrefresh

will automatically update (or refresh) your Mercurial Queue repository
with the new changes in your work directory. See the Mercurial Queues
documentation for more help using the ``qrefresh`` command. 

To create a new patch, use the ``hg qnew <PATCHNAME>`` command. 

Further readings
-----------------

See http://hgbook.red-bean.com/hgbookch12.html 

