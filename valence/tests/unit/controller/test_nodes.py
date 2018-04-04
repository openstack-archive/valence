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

from valence.common import exception
from valence.controller import nodes
from valence.podmanagers import podm_base
from valence.tests.unit.db import utils as test_utils
from valence.tests.unit.fakes import flavor_fakes
from valence.tests.unit.fakes import node_fakes


class TestAPINodes(unittest.TestCase):

    @mock.patch('valence.podmanagers.manager.get_connection')
    @mock.patch('valence.redfish.sushy.sushy_instance.RedfishInstance')
    def setUp(self, mock_redfish, mock_connection):
        self.node_controller = nodes.Node(podm_id='test-podm-1')
        self.node_controller.node = test_utils.get_test_composed_node_db_info()
        self.node_controller.connection = podm_base.PodManagerBase(
            'fake', 'fake-pass', 'http://fake-url')

    def test_show_node_brief_info(self):
        """Test only show node brief info"""
        node_info = node_fakes.get_test_composed_node()
        expected = {
            "index": "1",
            "name": "fake_name",
            "podm_id": "78e2a25-2901-438d-8157-de7ffd68d05",
            "uuid": "ea8e2a25-2901-438d-8157-de7ffd68d051",
            "resource_uri": 'nodes/7be5bc10-dcdf-11e6-bd86-934bc6947c55/',
        }
        self.assertEqual(expected,
                         nodes.Node._show_node_brief_info(node_info))

    @mock.patch("valence.db.api.Connection.create_composed_node")
    @mock.patch("valence.common.utils.generate_uuid")
    @mock.patch("valence.controller.nodes.Node.list_composed_nodes")
    @mock.patch("valence.podmanagers.podm_base.PodManagerBase.get_node_info")
    def test_manage_node(self, mock_get_node, mock_list_nodes,
                         mock_generate_uuid, mock_db_create_composed_node):
        manage_node = node_fakes.get_test_composed_node()
        manage_node['podm_id'] = 'test-podm-1'
        mock_get_node.return_value = manage_node
        node_list = node_fakes.get_test_node_list()
        # Change the index of node 1 so that the node to manage
        # doesn't appear in the list of nodes already managed by Valence.
        node_list[0]["index"] = '4'
        mock_list_nodes.return_value = node_list

        uuid = "ea8e2a25-2901-438d-8157-de7ffd68d051"
        mock_generate_uuid.return_value = uuid
        node_db = {"uuid": manage_node["uuid"],
                   "index": manage_node["index"],
                   "podm_id": manage_node["podm_id"],
                   "name": manage_node["name"],
                   "resource_uri": manage_node["resource_uri"]}

        req = {"node_index": "1"}
        self.node_controller.manage_node(req)
        mock_db_create_composed_node.assert_called_once_with(node_db)

    @mock.patch("valence.controller.nodes.Node.list_composed_nodes")
    def test_manage_already_managed_node(self, mock_list_nodes):
        # Leave the index of node 1 as '1' so that it conflicts with the node
        # being managed, meaning we're trying to manage a node that already
        # exists in the Valence DB.
        node_list = node_fakes.get_test_node_list()
        mock_list_nodes.return_value = node_list
        self.assertRaises(exception.ResourceExists,
                          self.node_controller.manage_node,
                          {"node_index": "1"})

    @mock.patch("valence.db.api.Connection.create_composed_node")
    @mock.patch("valence.common.utils.generate_uuid")
    @mock.patch("valence.podmanagers.podm_base.PodManagerBase.compose_node")
    def test_compose_node(self, mock_redfish_compose_node,
                          mock_generate_uuid,
                          mock_db_create_composed_node):
        """Test compose node successfully"""
        node_hw = node_fakes.get_test_composed_node()
        node_db = {"uuid": node_hw["uuid"],
                   "podm_id": 'test-podm-1',
                   "index": node_hw["index"],
                   "name": node_hw["name"],
                   "resource_uri": node_hw["resource_uri"]}

        compose_request = {'name': 'fake_name',
                           'description': 'fake_description'}
        mock_redfish_compose_node.return_value = node_hw
        uuid = 'ea8e2a25-2901-438d-8157-de7ffd68d051'
        mock_generate_uuid.return_value = uuid

        result = self.node_controller.compose_node(compose_request)
        expected = nodes.Node._show_node_brief_info(node_hw)

        self.assertEqual(expected, result)
        mock_db_create_composed_node.assert_called_once_with(node_db)

    @mock.patch("valence.db.api.Connection.create_composed_node")
    @mock.patch("valence.common.utils.generate_uuid")
    @mock.patch("valence.podmanagers.podm_base.PodManagerBase.compose_node")
    @mock.patch("valence.controller.flavors.get_flavor")
    def test_compose_node_with_flavor(self, mock_get_flavor,
                                      mock_redfish_compose_node,
                                      mock_generate_uuid,
                                      mock_db_create_composed_node):
        """Test node composition using a flavor for requirements"""
        node_hw = node_fakes.get_test_composed_node()
        node_db = {"uuid": node_hw["uuid"],
                   "podm_id": 'test-podm-1',
                   "index": node_hw["index"],
                   "name": node_hw["name"],
                   "resource_uri": node_hw["resource_uri"]}

        mock_redfish_compose_node.return_value = node_hw
        uuid = 'ea8e2a25-2901-438d-8157-de7ffd68d051'
        mock_generate_uuid.return_value = uuid

        flavor = flavor_fakes.fake_flavor()
        mock_get_flavor.return_value = flavor

        result = self.node_controller.compose_node(
            {"name": node_hw["name"],
             "description": node_hw["description"],
             "flavor_id": flavor["uuid"]})
        expected = nodes.Node._show_node_brief_info(node_hw)

        self.assertEqual(expected, result)
        mock_db_create_composed_node.assert_called_once_with(node_db)
        mock_get_flavor.assert_called_once_with(flavor["uuid"])

    @mock.patch("valence.podmanagers.podm_base.PodManagerBase.get_node_info")
    def test_get_composed_node_by_uuid(self, mock_redfish_get_node):
        """Test get composed node detail"""
        node_hw = node_fakes.get_test_composed_node()
        node_db = test_utils.get_test_composed_node_db_info()

        self.node_controller.node = node_db
        mock_redfish_get_node.return_value = node_hw

        result = self.node_controller.get_composed_node_by_uuid()
        expected = copy.deepcopy(node_hw)
        expected.update(node_db)
        self.assertEqual(expected, result)

    @mock.patch("valence.db.api.Connection.delete_composed_node")
    def test_delete_composed_node(self, mock_db_delete_composed_node):
        """Test delete composed node"""
        node_db = test_utils.get_test_composed_node_db_info()
        self.node_controller.node = node_db
        self.node_controller.delete_composed_node()
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

    @mock.patch("valence.podmanagers.podm_base.PodManagerBase.node_action")
    def test_node_action(self, mock_node_action):
        """Test reset composed node status"""
        action = {"Reset": {"Type": "On"}}
        self.node_controller.node = {'index': '1', 'name': 'test-node'}
        self.node_controller.node_action(action)
        mock_node_action.assert_called_once_with('1', action)

    @mock.patch("valence.provision.driver.node_register")
    def test_node_register(self, mock_node_register):
        nodes.Node.node_register("fake_uuid", {"foo": "bar"})
        mock_node_register.assert_called_once_with("fake_uuid", {"foo": "bar"})
