from six.moves import http_client

from valence.tests import FunctionalTest


class TestRootController(FunctionalTest):

    def test_root_get(self):
        response = self.app.get('/')
        assert response.status_code == http_client.OK

    def test_v1_get(self):
        response = self.app.get('/v1')
        assert response.status_code == http_client.OK
