import posixpath
import io

from notmm.utils.wsgilib import HTTPResponse
from threading import Lock
from .configuration import settings

lock = Lock()
def image_handler(request, *args, **kwds):
    #print args, kwds
    docroot = kwds.get('document_root', settings.MEDIA_ROOT)
    filename = posixpath.split(request.path_url)[-1]
    ext = filename.split('.')[-1]

    filename = posixpath.join(docroot, filename)

    lock.acquire()
    try:
        with io.open(filename, 'rb') as fdata:
            outbuf = fdata.read()
        lock.release()    
        headers = (
            ('Content-Type', "image/%s" % ext),
            ('Content-Length', str(len(outbuf)))
            )
    except (IOError,OSError):
        print('fatal error opening file: %s'%filename)
    return HTTPResponse(content=outbuf, headers=headers, force_unicode=False)

