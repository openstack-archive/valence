# copyright (c) 2016 Intel, Inc.
#
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
import unittest

import mock

from valence.controller import nodes
from valence.tests.unit.controller import fakes
from valence.tests.unit.db import utils as test_utils


class TestAPINodes(unittest.TestCase):

    def test_show_node_brief_info(self):
        """Test only show node brief info"""
        node_info = fakes.get_test_composed_node()
        expected = {
            "name": "fake_name",
            "uuid": "ea8e2a25-2901-438d-8157-de7ffd68d051",
            "links": [{'href': 'http://127.0.0.1:8181/v1/nodes/'
                               '7be5bc10-dcdf-11e6-bd86-934bc6947c55/',
                       'rel': 'self'},
                      {'href': 'http://127.0.0.1:8181/nodes/'
                               '7be5bc10-dcdf-11e6-bd86-934bc6947c55/',
                       'rel': 'bookmark'}]
        }
        self.assertEqual(expected,
                         nodes.Node._show_node_brief_info(node_info))

    def test_create_compose_request(self):
        name = "test_request"
        description = "request for testing purposes"
        requirements = {
            "memory": {
                "capacity_mib": "4000",
                "type": "DDR3"
            },
            "processor": {
                "model": "Intel",
                "total_cores": "4"
            }
        }

        expected = {
            "Name": "test_request",
            "Description": "request for testing purposes",
            "Memory": [{
                "CapacityMiB": "4000",
                "DimmDeviceType": "DDR3"
            }],
            "Processors": [{
                "Model": "Intel",
                "TotalCores": "4"
            }]
        }
        result = nodes.Node._create_compose_request(name,
                                                    description,
                                                    requirements)
        print(result)
        self.assertEqual(expected, result)

    @mock.patch("valence.db.api.Connection.create_composed_node")
    @mock.patch("valence.common.utils.generate_uuid")
    @mock.patch("valence.redfish.redfish.compose_node")
    def test_compose_node(self, mock_redfish_compose_node, mock_generate_uuid,
                          mock_db_create_composed_node):
        """Test compose node successfully"""
        node_hw = fakes.get_test_composed_node()
        node_db = {"uuid": node_hw["uuid"],
                   "index": node_hw["index"],
                   "name": node_hw["name"],
                   "links": node_hw["links"]}

        mock_redfish_compose_node.return_value = node_hw
        uuid = 'ea8e2a25-2901-438d-8157-de7ffd68d051'
        mock_generate_uuid.return_value = uuid

        result = nodes.Node.compose_node({"name": "test",
                                          "description": "test node",
                                          "properties": {}})
        expected = nodes.Node._show_node_brief_info(node_hw)

        self.assertEqual(expected, result)
        mock_db_create_composed_node.assert_called_once_with(node_db)

    @mock.patch("valence.redfish.redfish.get_node_by_id")
    @mock.patch("valence.db.api.Connection.get_composed_node_by_uuid")
    def test_get_composed_node_by_uuid(
            self, mock_db_get_composed_node, mock_redfish_get_node):
        """Test get composed node detail"""
        node_hw = fakes.get_test_composed_node()
        node_db = test_utils.get_test_composed_node_db_info()

        mock_db_model = mock.MagicMock()
        mock_db_model.as_dict.return_value = node_db
        mock_db_get_composed_node.return_value = mock_db_model

        mock_redfish_get_node.return_value = node_hw

        result = nodes.Node.get_composed_node_by_uuid("fake_uuid")

        expected = copy.deepcopy(node_hw)
        expected.update(node_db)
        self.assertEqual(expected, result)

    @mock.patch("valence.db.api.Connection.delete_composed_node")
    @mock.patch("valence.redfish.redfish.delete_composed_node")
    @mock.patch("valence.db.api.Connection.get_composed_node_by_uuid")
    def test_delete_composed_node(
            self, mock_db_get_composed_node, mock_redfish_delete_composed_node,
            mock_db_delete_composed_node):
        """Test delete composed node"""
        node_db = test_utils.get_test_composed_node_db_info()

        mock_db_model = mock.MagicMock()
        mock_db_model.index = node_db["index"]
        mock_db_get_composed_node.return_value = mock_db_model

        nodes.Node.delete_composed_node(node_db["uuid"])

        mock_redfish_delete_composed_node.assert_called_once_with(
            node_db["index"])
        mock_db_delete_composed_node.assert_called_once_with(
            node_db["uuid"])

    @mock.patch("valence.db.api.Connection.list_composed_nodes")
    def test_list_composed_nodes(self, mock_db_list_composed_nodes):
        """Test list all composed nodes"""
        node_db = test_utils.get_test_composed_node_db_info()

        mock_db_model = mock.MagicMock()
        mock_db_model.as_dict.return_value = node_db
        mock_db_list_composed_nodes.return_value = [mock_db_model]

        expected = [nodes.Node._show_node_brief_info(node_db)]

        result = nodes.Node.list_composed_nodes()

        self.assertEqual(expected, result)

    @mock.patch("valence.redfish.redfish.node_action")
    @mock.patch("valence.db.api.Connection.get_composed_node_by_uuid")
    def test_node_action(
            self, mock_db_get_composed_node, mock_node_action):
        """Test reset composed node status"""
        action = {"Reset": {"Type": "On"}}
        mock_db_model = mock.MagicMock()
        mock_db_model.index = "1"
        mock_db_get_composed_node.return_value = mock_db_model

        nodes.Node.node_action("fake_uuid", action)
        mock_node_action.assert_called_once_with("1", action)
