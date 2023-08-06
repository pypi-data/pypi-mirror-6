#!/usr/bin/env python
# Copyright (C) 2007-2011 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved
# <LICENSE=ISC>
#
"""Additional subclasses on top of the WSGIController request
handler.

"""
from notmm.controllers.wsgi import WSGIController

__all__ = ['LoggingController', 'ModelController']

class LoggingController(WSGIController):
    """
    WSGIController subclass with logging support for HTTP requests and
    responses (currently experimental/untested)
    """

    def __init__(self, *args, **kwargs):
        super(LoggingController, self).__init__(*args, **kwargs)

        ## Logging options
        ## Get the system logger if any is set
        ## Variables:
        ## ENABLE_LOGGING = Enables/Disables Logging facilities
        ## LOGGING_FORMAT = Format of emitted log record
        ## LOGGING_ERROR_LOG = Location (path) of the error_log file if not logging to syslog
        ## LOGGING_CALLBACK = function to emit log records (rootLogger)
        if 'ENABLE_LOGGING' in self.settings.__dict__:
            self.logging_enabled = getattr(self.settings, 'ENABLE_LOGGING', False)
            if 'logging_conf' in kwargs and logging_enabled:
                try:
                    self.log = getattr(kwargs['logging_conf'], settings.LOGGING_CALLBACK)
                except AttributeError:
                    # misconfigured logging module
                    raise
                else:
                    self.log.info("Logging subsystem initialized!")
        else:
            self.logging_enabled = False

class ModelController(LoggingController):
    """
    ModelController adds a generic ``model`` object to a derived
    LoggingController subclass.
    """
    query_set_cls = list

    def __init__(self, *args, **kwargs):
        """init the parent class"""
        super(ModelController, self).__init__(*args, **kwargs)
        self.models = self.query_set_cls()

    def get_models(self, app, import_func=__import__,
        import_kwargs={'globals': {}, 'locals': {}, 'fromlist': []}):
        """Returns a sequence of all model classes for the given application
        by looking up in the corresponding ``model.py`` module

        models = self.get_models('blogengine.contrib.feeds')
        for model in models:
            print model

        """
        objs = dir(\
            import_func(app, **import_kwargs)
            )
        for item in objs:
            self.models.append(item)

        return self.models
