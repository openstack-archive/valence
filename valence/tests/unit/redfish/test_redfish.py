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

import os
from unittest import TestCase

import mock
import requests
from requests import auth
from requests.compat import urljoin
from six.moves import http_client

from valence.common import constants
from valence.common import exception
from valence import config as cfg
from valence.redfish import redfish
from valence.tests.unit.fakes import redfish_fakes as fakes


class TestRedfish(TestCase):

    def test_get_rfs_url(self):
        cfg.podm_url = "https://127.0.0.1:8443"
        expected = urljoin(cfg.podm_url, "redfish/v1/Systems/1")

        # test without service_ext
        result = redfish.get_rfs_url("/Systems/1/")
        self.assertEqual(expected, result)

        result = redfish.get_rfs_url("/Systems/1")
        self.assertEqual(expected, result)

        result = redfish.get_rfs_url("Systems/1/")
        self.assertEqual(expected, result)

        result = redfish.get_rfs_url("Systems/1")
        self.assertEqual(expected, result)

        # test with service_ext
        result = redfish.get_rfs_url("/redfish/v1/Systems/1/")
        self.assertEqual(expected, result)

        result = redfish.get_rfs_url("/redfish/v1/Systems/1")
        self.assertEqual(expected, result)

        result = redfish.get_rfs_url("redfish/v1/Systems/1/")
        self.assertEqual(expected, result)

        result = redfish.get_rfs_url("redfish/v1/Systems/1")
        self.assertEqual(expected, result)

    def test_get_rfs_url_with_tailing_slash(self):
        cfg.podm_url = "https://127.0.0.1:8443/"
        expected = urljoin(cfg.podm_url, "redfish/v1/Systems/1")

        # test without service_ext
        result = redfish.get_rfs_url("/Systems/1/")
        self.assertEqual(expected, result)

        result = redfish.get_rfs_url("/Systems/1")
        self.assertEqual(expected, result)

        result = redfish.get_rfs_url("Systems/1/")
        self.assertEqual(expected, result)

        result = redfish.get_rfs_url("Systems/1")
        self.assertEqual(expected, result)

        # test with service_ext
        result = redfish.get_rfs_url("/redfish/v1/Systems/1/")
        self.assertEqual(expected, result)

        result = redfish.get_rfs_url("/redfish/v1/Systems/1")
        self.assertEqual(expected, result)

        result = redfish.get_rfs_url("redfish/v1/Systems/1/")
        self.assertEqual(expected, result)

        result = redfish.get_rfs_url("redfish/v1/Systems/1")
        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.send_request')
    def test_get_base_resource_url_chassis(self, mock_request):
        fake_resp = fakes.mock_request_get(fakes.fake_service_root(),
                                           http_client.OK)
        mock_request.return_value = fake_resp
        expected = "/redfish/v1/Chassis"
        result = redfish.get_base_resource_url("Chassis")
        self.assertEqual(expected, result)

    @mock.patch('requests.request')
    def test_send_request(self, mock_request):
        mock_request.return_value = "fake_node"
        result = redfish.send_request("Nodes/1")
        self.assertEqual("fake_node", result)

    @mock.patch('valence.redfish.redfish.send_request')
    def test_filter_chassis_rack(self, mock_request):
        fake_chassis_list = fakes.fake_chassis_list()
        first_request = fakes.mock_request_get(fake_chassis_list[0],
                                               http_client.OK)
        second_request = fakes.mock_request_get(fake_chassis_list[1],
                                                http_client.OK)
        third_request = fakes.mock_request_get(fake_chassis_list[2],
                                               http_client.OK)
        mock_request.side_effect = [first_request,
                                    second_request,
                                    third_request]
        chassis = {"Members":
                   [{"@odata.id": "1"},
                    {"@odata.id": "2"},
                    {"@odata.id": "3"}]}
        expected = {'Members': [
            {u'@odata.id': u'2'},
            {u'@odata.id': u'3'}
        ], 'Members@odata.count': 2}
        result = redfish.filter_chassis(chassis, "Rack")
        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.send_request')
    def test_urls2list_no_members(self, mock_request):
        resp = {"Name": "NoMembers", "Id": 1}
        mock_request.return_value = fakes.mock_request_get(resp,
                                                           http_client.OK)
        result = redfish.urls2list('/redfish/v1/test')
        self.assertEqual([], result)

    @mock.patch('valence.redfish.redfish.send_request')
    def test_urls2list_members(self, mock_request):
        resp = {"Name": "Members", "Id": 1,
                "Members":
                [{"@odata.id": "/redfish/v1/Member/1"},
                 {"@odata.id": "/redfish/v1/Member/2"}]}
        mock_request.return_value = fakes.mock_request_get(resp,
                                                           http_client.OK)
        expected = ["/redfish/v1/Member/1", "/redfish/v1/Member/2"]
        result = redfish.urls2list('/redfish/v1/test')
        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.urls2list')
    @mock.patch('valence.redfish.redfish.send_request')
    def test_system_cpu_details(self, mock_request, mock_url_list):
        fake_processor_list = fakes.fake_processor_list()
        mock_url_list.return_value = ["/redfish/v1/Systems/1",
                                      "/redfish/v1/Systems/2"]
        first_request = fakes.mock_request_get(fake_processor_list[0],
                                               http_client.OK)
        second_request = fakes.mock_request_get(fake_processor_list[1],
                                                http_client.OK)
        mock_request.side_effect = [first_request, second_request]
        expected = {"cores": "3", "arch": "x86", "model": "Intel Xeon"}
        result = redfish.system_cpu_details("/redfish/v1/Systems/test")
        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.send_request')
    def test_system_ram_details(self, mock_request):
        resp = fakes.fake_detailed_system()
        mock_request.return_value = fakes.mock_request_get(resp,
                                                           http_client.OK)
        expected = '8'
        result = redfish.system_ram_details("/redfish/v1/Systems/test")
        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.send_request')
    def test_system_network_details(self, mock_request):
        resp = fakes.fake_system_ethernet_interfaces()
        mock_request.return_value = fakes.mock_request_get(resp,
                                                           http_client.OK)
        expected = '2'
        result = redfish.system_network_details("/redfish/v1/Systems/test")
        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.urls2list')
    @mock.patch('valence.redfish.redfish.send_request')
    def test_system_storage_details(self, mock_request, mock_url_list):
        mock_url_list.return_value = ["/redfish/v1/Systems/1/SimpleStorage/1"]
        resp = fakes.fake_simple_storage()
        mock_request.return_value = fakes.mock_request_get(resp,
                                                           http_client.OK)
        expected = '600'
        result = redfish.system_storage_details("/redfish/v1/Systems/test")
        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.send_request')
    def test_show_cpu_details(self, mock_request):
        mock_request.return_value = fakes.mock_request_get(
            fakes.fake_processor(), http_client.OK)
        expected = {
            "instruction_set": "x86-64",
            "model": "Intel(R) Core(TM) i7-4790",
            "speed_mhz": 3700,
            "total_core": 8,
        }

        result = redfish.show_cpu_details("/redfish/v1/Systems/1/Processors/1")
        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.send_request')
    def test_show_memory_details(self, mock_request):
        mock_request.return_value = fakes.mock_request_get(
            fakes.fake_memory(), http_client.OK)
        expected = {
            "data_width_bit": 0,
            "speed_mhz": 2400,
            "total_memory_mb": 8192
        }

        result = redfish.show_ram_details("/redfish/v1/Systems/1/Memory/1")
        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.urls2list')
    @mock.patch('valence.redfish.redfish.send_request')
    def test_show_network_interface_details(self, mock_request, mock_url2list):
        mock_request.side_effect = [
            fakes.mock_request_get(fakes.fake_network_interface(),
                                   http_client.OK),
            fakes.mock_request_get(fakes.fake_vlan(),
                                   http_client.OK)
        ]
        mock_url2list.return_value = [
            "redfish/v1/Systems/1/EthernetInterfaces/2/VLANs/1"]
        expected = {
            "mac": "e9:47:d3:60:64:66",
            "speed_mbps": 100,
            "status": "Enabled",
            "ipv4": [{
                "address": "192.168.0.10",
                "subnet_mask": "255.255.252.0",
                "gateway": "192.168.0.1",
            }],
            'vlans': [{
                'status': 'Enabled',
                'vlanid': 99
            }]
        }

        result = redfish.show_network_details(
            "/redfish/v1/Systems/1/EthernetInterfaces/1")
        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.get_base_resource_url')
    @mock.patch('valence.redfish.redfish.send_request')
    def test_delete_composednode_ok(self, mock_request, mock_get_url):
        mock_get_url.return_value = '/redfish/v1/Nodes'
        delete_result = fakes.fake_delete_composednode_ok()
        fake_delete_response = fakes.mock_request_get(delete_result,
                                                      http_client.NO_CONTENT)
        mock_request.return_value = fake_delete_response
        result = redfish.delete_composed_node(101)
        mock_request.assert_called_with('/redfish/v1/Nodes/101', 'DELETE')
        expected = {
            "code": "DELETED",
            "detail": "This composed node has been deleted successfully.",
            "request_id": exception.FAKE_REQUEST_ID,
        }

        self.assertEqual(expected, result)

    @mock.patch('valence.common.utils.make_response')
    @mock.patch('valence.redfish.redfish.get_base_resource_url')
    @mock.patch('valence.redfish.redfish.send_request')
    def test_delete_composednode_fail(self, mock_request, mock_get_url,
                                      mock_make_response):
        mock_get_url.return_value = '/redfish/v1/Nodes'
        delete_result = fakes.fake_delete_composednode_fail()
        fake_resp = fakes.mock_request_get(delete_result,
                                           http_client.INTERNAL_SERVER_ERROR)
        mock_request.return_value = fake_resp
        self.assertRaises(exception.RedfishException,
                          redfish.delete_composed_node, 101)
        self.assertFalse(mock_make_response.called)

    @mock.patch('requests.get')
    def test_get_podm_status_Offline_by_wrong_auth(self, mock_get):
        fake_resp = fakes.mock_request_get({}, 401)
        mock_get.return_value = fake_resp
        self.assertEqual(redfish.pod_status('url', 'username', 'password'),
                         constants.PODM_STATUS_OFFLINE)
        mock_get.asset_called_once_with('url',
                                        auth=auth.HTTPBasicAuth('username',
                                                                'password'))

    @mock.patch('requests.get')
    def test_get_podm_status_Offline_by_http_exception(self, mock_get):
        mock_get.side_effect = requests.ConnectionError
        self.assertEqual(redfish.pod_status('url', 'username', 'password'),
                         constants.PODM_STATUS_OFFLINE)
        mock_get.asset_called_once_with('url',
                                        auth=auth.HTTPBasicAuth('username',
                                                                'password'))
        # SSL Error
        mock_get.side_effect = requests.exceptions.SSLError
        self.assertEqual(redfish.pod_status('url', 'username', 'password'),
                         constants.PODM_STATUS_OFFLINE)
        self.assertEqual(mock_get.call_count, 2)
        # Timeout
        mock_get.side_effect = requests.Timeout
        self.assertEqual(redfish.pod_status('url', 'username', 'password'),
                         constants.PODM_STATUS_OFFLINE)
        self.assertEqual(mock_get.call_count, 3)

    @mock.patch('requests.get')
    def test_get_podm_status_Online(self, mock_get):
        fake_resp = fakes.mock_request_get({}, http_client.OK)
        mock_get.return_value = fake_resp
        self.assertEqual(redfish.pod_status('url', 'username', 'password'),
                         constants.PODM_STATUS_ONLINE)
        mock_get.asset_called_once_with('url',
                                        auth=auth.HTTPBasicAuth('username',
                                                                'password'))

    @mock.patch('valence.redfish.redfish.get_base_resource_url')
    @mock.patch('valence.redfish.redfish.send_request')
    def test_allocate_node_conflict(self, mock_request, mock_get_url):
        """Test allocate resource conflict when compose node"""
        mock_get_url.return_value = '/redfish/v1/Nodes'

        # Fake response for getting nodes root
        fake_node_root_resp = fakes.mock_request_get(fakes.fake_nodes_root(),
                                                     http_client.OK)
        # Fake response for allocating node
        fake_node_allocation_conflict = \
            fakes.mock_request_get(fakes.fake_allocate_node_conflict(),
                                   http_client.CONFLICT)
        mock_request.side_effect = [fake_node_root_resp,
                                    fake_node_allocation_conflict]

        with self.assertRaises(exception.RedfishException) as context:
            redfish.compose_node({"name": "test_node"})

        self.assertTrue("There are no computer systems available for this "
                        "allocation request." in str(context.exception.detail))

    @mock.patch('valence.redfish.redfish.delete_composed_node')
    @mock.patch('valence.redfish.redfish.get_base_resource_url')
    @mock.patch('valence.redfish.redfish.send_request')
    def test_assemble_node_failed(self, mock_request, mock_get_url,
                                  mock_delete_node):
        """Test allocate resource conflict when compose node"""
        mock_get_url.return_value = '/redfish/v1/Nodes'

        # Fake response for getting nodes root
        fake_node_root_resp = fakes.mock_request_get(fakes.fake_nodes_root(),
                                                     http_client.OK)
        # Fake response for allocating node
        fake_node_allocation_conflict = mock.MagicMock()
        fake_node_allocation_conflict.status_code = http_client.CREATED
        fake_node_allocation_conflict.headers['Location'] = \
            os.path.normpath("/".join([cfg.podm_url, 'redfish/v1/Nodes/1']))

        # Fake response for getting url of node assembling
        fake_node_detail = fakes.mock_request_get(fakes.fake_node_detail(),
                                                  http_client.OK)

        # Fake response for assembling node
        fake_node_assemble_failed = fakes.mock_request_get(
            fakes.fake_assemble_node_failed(), http_client.BAD_REQUEST)
        mock_request.side_effect = [fake_node_root_resp,
                                    fake_node_allocation_conflict,
                                    fake_node_detail,
                                    fake_node_assemble_failed]

        with self.assertRaises(exception.RedfishException):
            redfish.compose_node({"name": "test_node"})

        mock_delete_node.assert_called_once()

    @mock.patch('valence.redfish.redfish.get_node_by_id')
    @mock.patch('valence.redfish.redfish.delete_composed_node')
    @mock.patch('valence.redfish.redfish.get_base_resource_url')
    @mock.patch('valence.redfish.redfish.send_request')
    def test_assemble_node_success(self, mock_request, mock_get_url,
                                   mock_delete_node, mock_get_node_by_id):
        """Test compose node successfully"""
        mock_get_url.return_value = '/redfish/v1/Nodes'

        # Fake response for getting nodes root
        fake_node_root_resp = fakes.mock_request_get(fakes.fake_nodes_root(),
                                                     http_client.OK)
        # Fake response for allocating node
        fake_node_allocation_conflict = mock.MagicMock()
        fake_node_allocation_conflict.status_code = http_client.CREATED
        fake_node_allocation_conflict.headers['Location'] = \
            os.path.normpath("/".join([cfg.podm_url, 'redfish/v1/Nodes/1']))

        # Fake response for getting url of node assembling
        fake_node_detail = fakes.mock_request_get(fakes.fake_node_detail(),
                                                  http_client.OK)

        # Fake response for assembling node
        fake_node_assemble_failed = fakes.mock_request_get(
            {}, http_client.NO_CONTENT)
        mock_request.side_effect = [fake_node_root_resp,
                                    fake_node_allocation_conflict,
                                    fake_node_detail,
                                    fake_node_assemble_failed]

        redfish.compose_node({"name": "test_node"})

        mock_delete_node.assert_not_called()
        mock_get_node_by_id.assert_called_once()

    @mock.patch('valence.redfish.redfish.get_node_by_id')
    @mock.patch('valence.redfish.redfish.urls2list')
    @mock.patch('valence.redfish.redfish.get_base_resource_url')
    def test_list_node(self, mock_get_url, mock_url2list, mock_get_node_by_id):
        """Test list node"""
        mock_get_url.return_value = '/redfish/v1/Nodes'
        mock_url2list.return_value = ['redfish/v1/Nodes/1']
        mock_get_node_by_id.side_effect = ["node1_detail"]

        result = redfish.list_nodes()

        mock_get_node_by_id.assert_called_with("1", show_detail=False)
        self.assertEqual(["node1_detail"], result)

    @mock.patch('valence.redfish.redfish.send_request')
    @mock.patch('valence.redfish.redfish.get_base_resource_url')
    def test_node_action_malformed_request(self, mock_get_url, mock_request):
        """Test reset node with malformed request content"""
        mock_get_url.return_value = '/redfish/v1/Nodes'
        mock_request.return_value = fakes.mock_request_get(
            fakes.fake_node_detail(), http_client.OK)

        with self.assertRaises(exception.BadRequest) as context:
            redfish.node_action("1", {"fake_request": "fake_value"})

        self.assertTrue("Please refer to Valence api specification to correct "
                        "this malformed content of node action request." in
                        str(context.exception.detail))

    @mock.patch('valence.redfish.redfish.send_request')
    @mock.patch('valence.redfish.redfish.get_base_resource_url')
    def test_node_action_wrong_request(self, mock_get_url, mock_request):
        """Test reset node with wrong action type"""
        mock_get_url.return_value = '/redfish/v1/Nodes'
        mock_request.return_value = fakes.mock_request_get(
            fakes.fake_node_detail(), http_client.OK)

        with self.assertRaises(exception.BadRequest) as context:
            redfish.node_action("1", {"Reset": {"Type": "wrong_action"}})

        self.assertTrue("Action type wrong_action is not in allowable action "
                        "list" in str(context.exception.detail))

    @mock.patch('valence.redfish.redfish.send_request')
    @mock.patch('valence.redfish.redfish.get_base_resource_url')
    def test_node_action_success(self, mock_get_url, mock_request):
        """Test successfully reset node status"""
        mock_get_url.return_value = '/redfish/v1/Nodes'
        fake_node_detail = fakes.mock_request_get(
            fakes.fake_node_detail(), http_client.OK)
        fake_node_action_resp = fakes.mock_request_get(
            {}, http_client.NO_CONTENT)
        mock_request.side_effect = [fake_node_detail, fake_node_action_resp]

        result = redfish.node_action("1", {"Reset": {"Type": "On"}})
        expected = exception.confirmation(
            confirm_code="Reset Composed Node",
            confirm_detail="This composed node has been set to On "
                           "successfully.")

        self.assertEqual(expected, result)
