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

    @mock.patch("valence.provision.ironic.utils.create_ironicclient")
    def setUp(self, mock_ironic_client):
        super(TestDriver, self).setUp()
        self.driver = driver.IronicDriver()
        self.driver.ironic = mock.MagicMock()

    def tearDown(self):
        super(TestDriver, self).tearDown()

    @mock.patch("valence.db.api.Connection.get_composed_node_by_uuid")
    def test_node_register_node_not_found(self, mock_db):
        mock_db.side_effect = exception.NotFound("node not found")
        self.assertRaises(exception.NotFound,
                          self.driver.node_register,
                          'fake-uuid', {})

    @mock.patch('valence.redfish.sushy.sushy_instance.RedfishInstance')
    @mock.patch("valence.db.api.Connection.update_composed_node")
    @mock.patch('valence.controller.nodes.Node')
    def test_node_register(self, node_mock, mock_node_update, mock_sushy):
        ironic = self.driver.ironic
        node_mock.return_value = mock.MagicMock()
        node_info = {
            'id': 'fake-uuid', 'podm_id': 'fake-podm_id',
            'index': '1',
            'name': 'test', 'metadata':
            {'network': [{'mac': 'fake-mac'}]},
            'computer_system': '/redfish/v1/Systems/437XR1138R2'}
        node_controller = node_mock.return_value
        node_controller.get_composed_node_by_uuid.return_value = node_info
        node_info.update({'managed_by': 'ironic'})
        mock_node_update.return_value.as_dict.return_value = node_info
        node_controller.connection = mock.MagicMock()
        ironic.node.create.return_value = mock.MagicMock(uuid='ironic-uuid')
        n_args = ({'driver_info': {'username': 'fake1'}}, {})
        node_controller.connection.get_ironic_node_params.return_value = n_args
        resp = self.driver.node_register('fake-uuid',
                                         {"extra": {"foo": "bar"}})
        self.assertEqual(node_info, resp)
        node_mock.assert_called_once_with(node_id='fake-uuid')
        mock_node_update.assert_called_once_with('fake-uuid',
                                                 {'managed_by': 'ironic'})
        ironic.node.create.assert_called_once()

    def test_ironic_port_create(self):
        port_args = {'mac_address': 'fake-mac'}
        self.driver.ironic_port_create(**port_args)
        self.driver.ironic.port.create.assert_called_once()
