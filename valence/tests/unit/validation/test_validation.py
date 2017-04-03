import json

import mock
from oslotest import base

from valence.api import app as flask_app
from valence.tests.unit.fakes import flavor_fakes


class TestApiValidation(base.BaseTestCase):
    """Test case base class for all unit tests."""

    def setUp(self):
        super(TestApiValidation, self).setUp()
        app = flask_app.get_app()
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.flavor = flavor_fakes.fake_flavor()

    @mock.patch('valence.controller.flavors.create_flavor')
    def test_flavor_create(self, mock_create):
        flavor = self.flavor
        flavor.pop('uuid')
        mock_create.return_value = self.flavor
        response = self.app.post('/v1/flavors',
                                 content_type='application/json',
                                 data=json.dumps(flavor))
        self.assertEqual(200, response.status_code)
        mock_create.assert_called_once_with(flavor)

    def test_flavor_create_incorrect_param(self):
        flavor = self.flavor
        flavor.pop('uuid')
        # Test invalid value
        flavor['properties']['memory']['capacity_mib'] = 10
        response = self.app.post('/v1/flavors',
                                 content_type='application/json',
                                 data=json.dumps(self.flavor))
        response = json.loads(response.data.decode())
        self.assertEqual(400, response['status'])
        self.assertEqual('ValidationError', response['code'])

        # Test invalid key
        flavor['properties']['invalid_key'] = 'invalid'
        response = self.app.post('/v1/flavors',
                                 content_type='application/json',
                                 data=json.dumps(self.flavor))
        response = json.loads(response.data.decode())
        self.assertEqual(400, response['status'])
        self.assertEqual('ValidationError', response['code'])
