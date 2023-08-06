# WSGI compat options:
# (pep333/pep3333/strictmode/django/paste)
# --wsgicompat=pep333  => default mode (use builtin wsgiref module)
# --wsgicompat=pep3333 => experimental python3 mode (untested)
# --wsgicompat=strict  => same as default mode (aka WSGI 1.0) [default]
# --wsgicompat=django  => django handler (experimental, may be buggy)
# --wsgicompat=paste => use paste as the server handler 

from test_support import (
    unittest,
    ResponseClass,
    RequestClass,
    TestClient,
    WSGIController
    )

class WSGIServerTestCase(unittest.TestCase):
    def setUp(self):
        self.content = b"1234"
        self.mimetype = 'text/plain'
        self.charset = 'utf8'
        self.wsgi_app = ResponseClass(self.content, \
            mimetype=self.mimetype, charset=self.charset)
        self.callback = WSGIController()
        self.client = TestClient(self.callback)
 

    def test_handle_one_request(self):
        response = self.client.get('/')
        self.assertEqual(response.status_int==200, True, response.status_int) 
