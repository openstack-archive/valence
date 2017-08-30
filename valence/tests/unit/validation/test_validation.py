# Copyright (c) 2017 NEC, Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import copy
import json

import mock
from oslotest import base
from six.moves import http_client

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
        self.assertEqual(http_client.OK, response.status_code)
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
        self.assertEqual(http_client.BAD_REQUEST, response['status'])
        self.assertEqual('Validation Error', response['title'])

        # Test invalid key
        flavor['properties']['invalid_key'] = 'invalid'
        response = self.app.post('/v1/flavors',
                                 content_type='application/json',
                                 data=json.dumps(self.flavor))
        response = json.loads(response.data.decode())
        self.assertEqual(http_client.BAD_REQUEST, response['status'])
        self.assertEqual('Validation Error', response['title'])


class TestPodmanagerApi(TestApiValidation):

    @mock.patch('valence.controller.podmanagers.create_podmanager')
    @mock.patch('valence.controller.podmanagers.get_podm_list')
    @mock.patch('valence.podmanagers.podm_base.PodManagerBase.get_status')
    def test_podmanager_create(self, pstatus_mock, plist_mock, pcreate_mock):
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
        result = copy.deepcopy(values)
        result['status'] = constants.PODM_STATUS_ONLINE
        pcreate_mock.return_value = result
        response = self.app.post('/v1/pod_managers',
                                 content_type='application/json',
                                 data=json.dumps(values))
        self.assertEqual(http_client.OK, response.status_code)

    def test_check_creation_incomplete_parameters(self):
        incomplete_values = {
            'name': 'name',
            'url': 'url'
        }
        response = self.app.post('/v1/pod_managers',
                                 content_type='application/json',
                                 data=json.dumps(incomplete_values))
        response = json.loads(response.data.decode())
        self.assertEqual(http_client.BAD_REQUEST, response['status'])
        self.assertEqual('Validation Error', response['title'])

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
        self.assertEqual(http_client.BAD_REQUEST, response['status'])
        self.assertEqual('Validation Error', response['title'])


@mock.patch('valence.podmanagers.manager.get_connection')
class TestNodeApi(TestApiValidation):

    @mock.patch('valence.controller.nodes.Node.compose_node')
    def test_compose_request_using_properties(self, mock_compose, mock_conn):
        req = {
            "name": "test_request",
            "podm_id": "test-podm",
            "properties": {
                "memory": {
                    "capacity_mib": "4000",
                    "type": "DDR3"
                },
                "processor": {
                    "model": "Intel",
                    "total_cores": "4"
                }
            }
        }
        mock_compose.return_value = req
        resp = self.app.post('/v1/nodes',
                             content_type='application/json',
                             data=json.dumps(req))
        mock_conn.assert_called_once_with('test-podm')
        self.assertEqual(http_client.OK, resp.status_code)

    @mock.patch('valence.controller.nodes.Node.compose_node')
    def test_compose_request_using_flavor(self, mock_compose, mock_connection):
        req = {
            "name": "test_request1",
            "flavor_id": "test_flavor",
            "podm_id": "test-podm-1"
        }
        mock_compose.return_value = req
        resp = self.app.post('/v1/nodes',
                             content_type='application/json',
                             data=json.dumps(req))
        mock_connection.assert_called_once_with('test-podm-1')
        self.assertEqual(http_client.OK, resp.status_code)

    def test_compose_request_invalid_params(self, mock_conn):
        req = {
            "name": "test_request1",
            "properties": {"invalid_key": "invalid_value"}
        }
        resp = self.app.post('/v1/nodes',
                             content_type='application/json',
                             data=json.dumps(req))
        response = json.loads(resp.data.decode())
        self.assertEqual(http_client.BAD_REQUEST, response['status'])
        self.assertEqual('Validation Error', response['title'])

    @mock.patch('valence.controller.nodes.Node.manage_node')
    def test_node_manage_request(self, mock_manage, mock_connection):
        req = {"node_index": "fake-index",
               "podm_id": "test-podm-id"}
        mock_manage.return_value = {"uuid": "ea8e2a25-2901-438d-8157-de7ffd",
                                    "links": "fake-links",
                                    "name": "fake-node",
                                    "index": "fake-index",
                                    "podm_id": "test-podm-id"}
        resp = self.app.post('/v1/nodes/manage',
                             content_type='application/json',
                             data=json.dumps(req))
        mock_connection.assert_called_once_with('test-podm-id')
        mock_manage.assert_called_once_with(req)
        self.assertEqual(http_client.OK, resp.status_code)

    def test_node_manage_request_invalid(self, mock_conn):
        req = {"node_id": "fake-index"}
        resp = self.app.post('/v1/nodes/manage',
                             content_type='application/json',
                             data=json.dumps(req))
        response = json.loads(resp.data.decode())
        self.assertEqual(http_client.BAD_REQUEST, response['status'])
        self.assertEqual('Validation Error', response['title'])

    @mock.patch('valence.db.api.Connection.get_composed_node_by_uuid')
    @mock.patch('valence.controller.nodes.Node.node_action')
    def test_node_action_request(self, mock_action, m_node, mock_connection):
        req = {
            "Reset": {
                "Type": "On"
            }
        }
        mock_action.return_value = None
        resp = self.app.post('/v1/nodes/fake-node/action',
                             content_type='application/json',
                             data=json.dumps(req))
        mock_action.assert_called_once_with(req)
        self.assertEqual(http_client.NO_CONTENT, resp.status_code)

    @mock.patch('valence.controller.nodes.Node.node_action')
    @mock.patch('valence.db.api.Connection.get_composed_node_by_uuid')
    def test_node_action_attach_request(self, mock_node, mock_action,
                                        mock_connection):
        req = {
            "attach": {
                "resource_id": "test-device-1"
            }
        }
        mock_action.return_value = None
        resp = self.app.post('/v1/nodes/fake-node/action',
                             content_type='application/json',
                             data=json.dumps(req))
        mock_action.assert_called_once_with(req)
        self.assertEqual(http_client.NO_CONTENT, resp.status_code)

    @mock.patch('valence.controller.nodes.Node.node_action')
    @mock.patch('valence.db.api.Connection.get_composed_node_by_uuid')
    def test_node_action_detach_request(self, mock_node, mock_action,
                                        mock_connection):
        req = {
            "detach": {
                "resource_id": "test-device-1"
            }
        }
        mock_action.return_value = None
        resp = self.app.post('/v1/nodes/fake-node/action',
                             content_type='application/json',
                             data=json.dumps(req))
        mock_action.assert_called_once_with(req)
        self.assertEqual(http_client.NO_CONTENT, resp.status_code)

    @mock.patch('valence.db.api.Connection.get_composed_node_by_uuid')
    def test_node_action_request_invalid(self, mock_node, mock_connection):
        req = {
            "Boot": {
                "Type": "On"
            }
        }
        resp = self.app.post('/v1/nodes/fake-node/action',
                             content_type='application/json',
                             data=json.dumps(req))
        response = json.loads(resp.data.decode())
        self.assertEqual(http_client.BAD_REQUEST, response['status'])
        self.assertEqual('Validation Error', response['title'])
