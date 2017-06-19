# Copyright 2016 Intel.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock

from oslotest import base

from valence.common import exception
from valence.provision.ironic import driver


class TestDriver(base.BaseTestCase):
    def setUp(self):
        super(TestDriver, self).setUp()
        self.ironic = driver.IronicDriver()

    def tearDown(self):
        super(TestDriver, self).tearDown()

    @mock.patch("valence.controller.nodes.Node.get_composed_node_by_uuid")
    def test_node_register_node_not_found(self, mock_db):
        mock_db.side_effect = exception.NotFound
        self.assertRaises(exception.NotFound,
                          self.ironic.node_register,
                          'fake-uuid', {})

    @mock.patch("valence.controller.nodes.Node.get_composed_node_by_uuid")
    @mock.patch("valence.provision.ironic.utils.create_ironicclient")
    def test_node_register_ironic_client_failure(self, mock_client,
                                                 mock_db):
        mock_client.side_effect = Exception()
        self.assertRaises(exception.ValenceException,
                          self.ironic.node_register,
                          'fake-uuid', {})

    @mock.patch("valence.db.api.Connection.update_podm_resource")
    @mock.patch("valence.controller.nodes.Node.get_composed_node_by_uuid")
    @mock.patch("valence.provision.ironic.utils.create_ironicclient")
    def test_node_register(self, mock_client,
                           mock_node_get, mock_resource_update):
        ironic = mock.MagicMock()
        mock_client.return_value = ironic
        mock_node_get.return_value = {
            'name': 'test', 'metadata':
            {'network': [{'mac': 'fake-mac'}]},
            'computer_system': '/redfish/v1/Systems/437XR1138R2'}
        ironic.node.create.return_value = mock.MagicMock(uuid='ironic-uuid')
        port_arg = {'node_uuid': 'ironic-uuid', 'address': 'fake-mac'}
        resp = self.ironic.node_register('fake-uuid',
                                         {"extra": {"foo": "bar"}})
        self.assertEqual({
            'code': 'Node Registered',
            'detail': 'The composed node fake-uuid has been '
                      'registered with Ironic successfully.',
            'request_id': '00000000-0000-0000-0000-000000000000'}, resp)
        mock_client.assert_called_once()
        mock_node_get.assert_called_once_with('fake-uuid')
        mock_resource_update.assert_called_once_with('fake-uuid',
                                                     {'managed_by': 'ironic'})
        ironic.node.create.assert_called_once()
        ironic.port.create.assert_called_once_with(**port_arg)
