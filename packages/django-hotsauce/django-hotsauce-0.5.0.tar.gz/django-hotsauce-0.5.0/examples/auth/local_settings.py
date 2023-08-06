import os
import os.path

ROOTDIR = os.environ['ROOTDIR']
MEDIA_ROOT = ROOTDIR

# List of processors used by RequestContext to populate the context.
# Each one should be a callable that takes the request object as its
# only parameter and returns a dictionary to add to the context.
TEMPLATE_CONTEXT_PROCESSORS = ()
MIDDLEWARE_CLASSES = ()
DEBUG = True
SECRET_KEY = 12348910

CUSTOM_ERROR_HANDLERS = (
    ('handle500', 'views.common.handle500'),
    ('handle404', 'views.common.handle404'),
    )

TEMPLATE_DIRS = (
    os.path.join(ROOTDIR, 'templates'),
)

ROOT_URLCONF = 'urls'

LOGGING_ERROR_LOG = os.path.join(ROOTDIR, 'error_log')

