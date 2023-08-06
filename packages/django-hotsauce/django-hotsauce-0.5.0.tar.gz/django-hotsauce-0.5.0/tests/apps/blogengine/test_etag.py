  # Add the Last-Modified HTTP header to support built-in 
    # conditional requests.
    _last_modified = ('Last-Modified', last_modified(t.last_modified))
    # And the ETag 
    #etag = ('ETag', hashlib.md5(_last_modified[1]).hexdigest())
    header_set = []
    ResponseHandler = HTTPResponse
    status_code = 200
    if 'ETag' in request.environ and request.environ['ETag'] == etag[1]:
        # Document is cached
        status_code = 304
        ResponseHandler = HTTPNotModifiedResponse


    if settings.ENABLE_TIDYLIB != False:
        # Clean up the HTML with tidylib
        from notmm.utils.markup import clean_html_document
        chunk, errors = clean_html_document(chunk)
        #if errors and settings.DEBUG:
        #    print(errors)
        del errors

