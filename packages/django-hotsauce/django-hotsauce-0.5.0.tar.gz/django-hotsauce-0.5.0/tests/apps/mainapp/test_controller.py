import sys
#import mainapp

from test_support import (
    WSGIControllerTestCase, 
    TestClient, 
    unittest,
    make_app,
    settings
    )

class WSGIAppTestCase(WSGIControllerTestCase):

    def test_render_index(self):
        req = self.client.request
        #import pdb; pdb.set_trace()
        response = self.client.get('/blog/') # 
        self.assertEqual(response.status_code, '200 OK')

