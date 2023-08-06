Cookie handling based on paste.auth.auth_tkt but with some bug fixes and
improvements

Supported cookie options (described in detail in the AuthKit manual)::
    
    cookie_name
    cookie_secure
    cookie_includeip
    cookie_signoutpath
    cookie_secret
    cookie_enforce_expires
    cookie_params = expires 
                    path 
                    comment 
                    domain 
                    max-age 
                    secure 
                    version 

Supported in the middleware but not yet used::
    
    tokens=() 
    user_data=''
    time=None

Features compared to the original paste version:

    #. The authenticate middleware should use authkit version of make_middleware
    #. We need the BadTicket handling in place
    #. We need to be able to use a custom AuthTicket
    #. The custom AuthTicket should accept cookie params specifiable in the 
       config file
    #. The cookie timestamp should be available in the environment as
       paste.auth_tkt.timestamp

.. Warning ::
    
    You shouldn't rely on the bad ticket or server side expires code because 
    when they are triggered, the sign in form isn't displayed. 
    
    Instead it is better to let the cookie expire naturally. For this reason 
    the server side expiration allows a second longer than the cookie expire 
    time so it only kicks in if the cookie fails to expire.
    
Here is an example:

.. code-block :: Python

    from paste.httpserver import serve
    from authkit.authenticate import middleware, test_app

    def valid(environ, username, password):
        return username==password

    app = middleware(
        test_app,
        method='form',
        cookie_secret='secret encryption string',
        valid=valid,
        cookie_signoutpath = '/signout',
        cookie_params = '''
            expires:10
            comment:test cookie
        ''',
        cookie_enforce = True
    )
    serve(app)

.. warning ::

    The username of the REMOTE_USER variable is stored in plain text in the cookie and
    so is any user data you specify so you should be aware of these facts and
    design your application accordingly. In particular you should definitely
    not store passwords as user data.


Bad Cookie Support
==================

If a cookie has expired or because there is an error parsing the ticket, it 
is known as a bad cookie. By default, a simple HTML page is displayed with
the title "Bad Cookie" and a brief message. The headers sent with this page 
remove the cookie.

You may want to disable this functionality and let your application handle
the error condition. You can do so with this option::

    authkit.cookie.badcookie.page = false

When a bad cookie is found the variable ``authkit.cookie.error`` is set in
the environment with a value ``True``. If the error was due to cookie
expiration the value ``authkit.cookie.timeout`` is also set to ``True``. It
is then up to your application to set an appropriate cookie or restrict 
access to resources. AuthKit will also remove any ``REMOTE_USER`` present. 

Rather than handling the bad cookie in your application you may just want 
to change the template used by AuthKit. You do so like this::

    authkit.cookie.badcookie.page = false
    authkit.cookie.badcookie.template.string = <html>Bad Cookie</html>

You can use any of the template options you use to customise a form so
you can also specify a function to render the template::

    authkit.cookie.badcookie.page = false
    authkit.cookie.badcookie.template.obj = mymodule.auth:render_badcookie

The render function can also take optional ``environ`` and ``state`` 
arguments which are passed in by AuthKit if the function takes them as named
arguments.

One thing to be aware of when using this functionality is that because the
render function gets called as the request is first passed along the middleware
chain, many of the tools your application relies on are not yet set up so 
you may not be able to use all the tools you usually do. This is unlike
thr forms situation where the form render function is called on the response
after all your usual application infrastructure is in place.

