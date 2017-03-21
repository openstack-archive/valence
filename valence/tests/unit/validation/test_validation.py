import json

import mock
from oslotest import base

from valence.api import app as flask_app
from valence.common import constants
from valence.tests.unit.fakes import flavor_fakes


class TestApiValidation(base.BaseTestCase):
    """Test case base class for all unit tests."""

    def setUp(self):
        super(TestApiValidation, self).setUp()
        app = flask_app.get_app()
        app.config['TESTING'] = True
        self.app = app.test_client()


class TestFlavorApi(TestApiValidation):
    def setUp(self):
        super(TestFlavorApi, self).setUp()
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


class TestPodmanagerApi(TestApiValidation):

    @mock.patch('valence.controller.podmanagers.get_podm_list')
    @mock.patch('valence.controller.podmanagers.get_podm_status')
    def test_podmanager_create(self, pstatus_mock, plist_mock):
        pstatus_mock.return_value = constants.PODM_STATUS_ONLINE
        plist_mock.return_value = []
        values = {
            "name": "podm_name",
            "url": "https://10.240.212.123",
            "authentication": [
                {
                    "type": "basic",
                    "auth_items":
                    {
                        "username": "xxxxxxx",
                        "password": "xxxxxxx"
                    }
                }]
            }
        response = self.app.post('/v1/pod_managers',
                                 content_type='application/json',
                                 data=json.dumps(values))
        self.assertEqual(200, response.status_code)

    def test_check_creation_incomplete_parameters(self):
        incomplete_values = {
            'name': 'name',
            'url': 'url'
        }
        response = self.app.post('/v1/pod_managers',
                                 content_type='application/json',
                                 data=json.dumps(incomplete_values))
        response = json.loads(response.data.decode())
        self.assertEqual(400, response['status'])
        self.assertEqual('ValidationError', response['code'])

    def test_check_creation_invalid_authentication(self):
        invalid_auth_values = {
            "name": "podm_name",
            "url": "https://10.0.0.2",
            'authentication': {
                "username": "username",
                "password": "password"
            }
        }
        response = self.app.post('/v1/pod_managers',
                                 content_type='application/json',
                                 data=json.dumps(invalid_auth_values))
        response = json.loads(response.data.decode())
        self.assertEqual(400, response['status'])
        self.assertEqual('ValidationError', response['code'])
