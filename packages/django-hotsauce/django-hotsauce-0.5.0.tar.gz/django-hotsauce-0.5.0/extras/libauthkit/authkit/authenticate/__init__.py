from base import *
from auth_tkt import AuthTKTMiddleware

def sample_app(environ, start_response):
    if environ.get('PATH_INFO') == '/403':
        start_response('403 Forbidden', [('Content-type', content_type)])
        return ['Access denied']
    elif environ.get('PATH_INFO') == '/401':
        start_response('401 Unauth', [('Content-type', content_type)])
        return ['Not Authenticated']
    elif environ.get('PATH_INFO') == '/702':
        start_response('702 Doesnt exist', [('Content-type', content_type)])
        return ['Access denied']
    elif environ.get('PATH_INFO') == '/500':
        start_response('500 Error', [('Content-type', content_type)])
        return ['Internal Server Error']

