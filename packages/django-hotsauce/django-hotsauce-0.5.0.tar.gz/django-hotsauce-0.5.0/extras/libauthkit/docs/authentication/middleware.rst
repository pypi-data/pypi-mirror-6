"""Authentication middleware

This module provides the ``authkit.authenticate.middleware`` middleware which is used to 
intercept responses with a specified status code, present a user with a means of authenticating 
themselves and handle the sign in process.

Each of the authentication methods supported by the middleware is described in
detail in the main AuthKit manual. The methods include:

* HTTP Basic (``basic``)
* HTTP Digest (``digest``)
* OpenID Passurl (``openid``)
* Form and Cookie (``form``)
* Forward (``forward``)
* Redirect (``redirect``)

The authenticate middleware can be configured directly or by means of a Paste
deploy config file as used by Pylons. It can be used directly like this:

.. code-block:: Python

    from authkit.authenticate import middleware, test_app
    from paste.httpserver import serve

    import sys
    app = middleware(
        test_app,
        enable = True,
        method = 'passurl',
        cookie_secret='some_secret',
    )
    
    serve(app, host='0.0.0.0', port=8000)

"""

