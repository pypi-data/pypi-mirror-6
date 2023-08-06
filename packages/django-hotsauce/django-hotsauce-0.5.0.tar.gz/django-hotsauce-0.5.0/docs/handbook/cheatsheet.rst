Tips and Tricks
================

:Last modified: 2010-07-12
:Author: Etienne Robillard <erob@gthcfoundation.org>
:Version: 0.4.1

The following list proposes simple tips and tricks for 
working with the notmm toolkit. Most of them can be used
in standard Django apps with moderate efforts to boost your 
productivity while making kick-ass websites.

Enabling Django Maintainer Mode
--------------------------------

To enable *Django Maintainer Mode* and impress your relatives in three 
steps:

1. Update Django to the latest available revision.
2. Apply the patch named 007_setup_environ.patch.  
3. Add the following lines in your ``~/.profile`` script::

 $ DJANGO_HOME=/some/path/to/django-1.0;
 $ PYTHONPATH="$DJANGO_HOME"
 $ DJANGO_SETTINGS_MODULE='myapp.settings'; 
 $ export DJANGO_HOME PYTHONPATH DJANGO_SETTINGS_MODULE

SQLAlchemy integration
-----------------------

Here's a simple recipe which uses SQLAlchemy and
the ``with_session`` decorator to make a custom SQL 
query in a standard Django view. ::

    from wsgiapp.views import render_to_response
    from notmm.utils.decorators import with_session
    from myapp.config import database as db

    @with_session(engine=db.engine)     
    def index(request):
        # get the ScopedSession instance
        Session = request.environ.get('_scoped_session')
        # now do something with the Session 
        data = {
          'user' : Session.query('User').filter_by(...).first()
          }
        # close the session  
        Session.close()

        return render_to_response(request, extra_context=data)

Lazier Django Settings
-----------------------

Here is an example using thread-local as a way to 
store custom data ::

    from notmm.datastore.threadlocal import LocalStore
    
    class LocalSettings(LocalStore):
        def __init__(self, **kwargs):
            LocalStore.__init__(self, **kwargs)
    
    # then simply initialize the LocalSettings object
    # for getting a Django-like settings module.
    settings = LocalSettings(favorite_color="magenta")
    # load settings from this module
    settings.loads('myapp.settings')
    settings.clear()  # remove all settings and set initialized=False
    settings.count()  # return a int

Alternatively, the ``LocalSettings`` class has now been replaced by
the ``notmm.utils.django_settings.SettingsProxy`` class. So here's a tip for
using ``SettingsProxy`` as a drop-in replacement for the code above ::

    from notmm.utils.django_settings import LazySettings
    settings = LazySettings()

