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

import mock
from unittest import TestCase

from valence import config as cfg
from valence.common import exception
from valence.redfish import redfish
from valence.tests.unit import fakes


class TestRedfish(TestCase):

    def test_get_rfs_url_no_service_ext(self):
        expected = cfg.podm_url + "/redfish/v1/Systems/1"
        result = redfish.get_rfs_url("Systems/1")
        self.assertEqual(expected, result)

    def test_get_rfs_url_with_service_ext(self):
        expected = cfg.podm_url + "/redfish/v1/Systems/1"
        result = redfish.get_rfs_url("/redfish/v1/Systems/1")
        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.send_request')
    def test_get_base_resource_url_chassis(self, mock_request):
        fake_resp = fakes.mock_request_get(fakes.fake_service_root(), "200")
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
        first_request = fakes.mock_request_get(fake_chassis_list[0], "200")
        second_request = fakes.mock_request_get(fake_chassis_list[1], "200")
        third_request = fakes.mock_request_get(fake_chassis_list[2], "200")
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
        mock_request.return_value = fakes.mock_request_get(resp, "200")
        result = redfish.urls2list('/redfish/v1/test')
        self.assertEqual([], result)

    @mock.patch('valence.redfish.redfish.send_request')
    def test_urls2list_members(self, mock_request):
        resp = {"Name": "Members", "Id": 1,
                "Members":
                [{"@odata.id": "/redfish/v1/Member/1"},
                 {"@odata.id": "/redfish/v1/Member/2"}]}
        mock_request.return_value = fakes.mock_request_get(resp, "200")
        expected = ["/redfish/v1/Member/1", "/redfish/v1/Member/2"]
        result = redfish.urls2list('/redfish/v1/test')
        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.urls2list')
    @mock.patch('valence.redfish.redfish.send_request')
    def test_system_cpu_details(self, mock_request, mock_url_list):
        fake_processor_list = fakes.fake_processor_list()
        mock_url_list.return_value = ["/redfish/v1/Systems/1",
                                      "/redfish/v1/Systems/2"]
        first_request = fakes.mock_request_get(fake_processor_list[0], "200")
        second_request = fakes.mock_request_get(fake_processor_list[1], "200")
        mock_request.side_effect = [first_request, second_request]
        expected = {"cores": "3", "arch": "x86", "model": "Intel Xeon"}
        result = redfish.system_cpu_details("/redfish/v1/Systems/test")
        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.send_request')
    def test_system_ram_details(self, mock_request):
        resp = fakes.fake_detailed_system()
        mock_request.return_value = fakes.mock_request_get(resp, "200")
        expected = '8'
        result = redfish.system_ram_details("/redfish/v1/Systems/test")
        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.send_request')
    def test_system_network_details(self, mock_request):
        resp = fakes.fake_system_ethernet_interfaces()
        mock_request.return_value = fakes.mock_request_get(resp, "200")
        expected = '2'
        result = redfish.system_network_details("/redfish/v1/Systems/test")
        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.urls2list')
    @mock.patch('valence.redfish.redfish.send_request')
    def test_system_storage_details(self, mock_request, mock_url_list):
        mock_url_list.return_value = ["/redfish/v1/Systems/1/SimpleStorage/1"]
        resp = fakes.fake_simple_storage()
        mock_request.return_value = fakes.mock_request_get(resp, "200")
        expected = '600'
        result = redfish.system_storage_details("/redfish/v1/Systems/test")
        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.get_base_resource_url')
    @mock.patch('valence.redfish.redfish.send_request')
    def test_delete_composednode_ok(self, mock_request, mock_get_url):
        mock_get_url.return_value = '/redfish/v1/Nodes'
        delete_result = fakes.fake_delete_composednode_ok()
        mock_request.return_value = fakes.mock_request_get(delete_result, 204)
        resp, status_code = redfish.delete_composednode(101)
        mock_request.assert_called_with('/redfish/v1/Nodes/101', 'DELETE')
        expected_resp = {
            "code": "",
            "details": "DELETED",
            "request_id": "00000000-0000-0000-0000-000000000000",
        }
        self.assertEqual(resp, expected_resp)
        self.assertEqual(status_code, 200)

    @mock.patch('valence.redfish.redfish.get_base_resource_url')
    @mock.patch('valence.redfish.redfish.send_request')
    def test_delete_composednode_ok(self, mock_request, mock_get_url):
        mock_get_url.return_value = '/redfish/v1/Nodes'
        delete_result = fakes.fake_delete_composednode_fail()
        mock_request.return_value = fakes.mock_request_get(delete_result, 500)
        self.assertRaises(exception.RedfishException, redfish.delete_composednode, 101)
