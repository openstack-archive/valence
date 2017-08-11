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
import valence.conf
from valence.redfish import redfish
from valence.tests.unit.fakes import redfish_fakes as fakes

CONF = valence.conf.CONF


class TestRedfish(TestCase):

    def test__parse_connection_info(self):
        CONF.podm.url = "https://127.0.0.1:8443"
        CONF.podm.username = "foo"
        CONF.podm.password = "bar"
        CONF.podm.root_prefix = "/redfish/v1"
        expected = {
            "base_url": "https://127.0.0.1:8443",
            "username": "foo",
            "password": "bar",
            "root_prefix": "/redfish/v1/"
        }
        result = redfish._parse_connection_info()
        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish._parse_connection_info')
    @mock.patch('valence.redfish.redfish.rsd_lib')
    def test_systems_list(self, mock_rsd_lib, mock_connection_info):
        mock_connection_info.return_value = {
            "base_url": "https://127.0.0.1:8443",
            "username": "foo",
            "password": "bar",
            "root_prefix": "/redfish/v1/"
        }
        fake_system_col = fakes.fake_system_col()
        fake_conn = mock_rsd_lib.RSDLib.return_value
        fake_conn.get_system_collection.return_value = fake_system_col
        expected = [
            {
                "identity": 1,
                "name": "System One",
                "power_state": "fake_power_state"
            },
            {
                "identity": 2,
                "name": "System Two",
                "power_state": "fake_power_state"
            }
        ]
        response = redfish.systems_list()
        self.assertEqual(expected, response)
        fake_conn.get_system_collection.assert_called_once()

    @mock.patch('valence.redfish.redfish._parse_connection_info')
    @mock.patch('valence.redfish.redfish.rsd_lib')
    def test_get_system(self, mock_rsd_lib, mock_connection_info):
        mock_connection_info.return_value = {
            "base_url": "https://127.0.0.1:8443",
            "username": "foo",
            "password": "bar",
            "root_prefix": "/redfish/v1/"
        }
        fake_system = fakes.fake_system(1, "System One")
        fake_conn = mock_rsd_lib.RSDLib.return_value
        fake_conn.get_system.return_value = fake_system
        expected = {
            "asset_tag": "fake_asset_tag",
            "bios_version": "fake_bios_version",
            "boot_enabled": "fake_boot_enabled",
            "boot_mode": "fake_boot_mode",
            "boot_target": "fake_boot_target",
            "description": "fake_description",
            "hostname": "fake_hostname",
            "identity": 1,
            "indicator_led": "fake_indicator_led",
            "manufacturer": "fake_manufacturer",
            "name": "System One",
            "part_number": "fake_part_number",
            "power_state": "fake_power_state",
            "serial_number": "fake_serial_number",
            "sku": "fake_sku",
            "memory_health": "fake_memory_health",
            "memory_size_gib": "fake_memory_size_gib",
            "processor_count": "fake_processor_count",
            "processor_architecture": "fake_processor_architecture"
        }
        response = redfish.get_system("1")
        self.assertEqual(expected, response)
        fake_conn.get_system.assert_called_once_with(
            "https://127.0.0.1:8443/redfish/v1/Systems/1")

    def test_get_rfs_url(self):
        CONF.podm.url = "https://127.0.0.1:8443"
        expected = urljoin(CONF.podm.url, "redfish/v1/Systems/1")

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
        CONF.podm.url = "https://127.0.0.1:8443/"
        expected = urljoin(CONF.podm.url, "redfish/v1/Systems/1")

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
        expected = [
            {
                "ChassisType": "Rack",
                "Name": "Rack 1",
                "Id": "2"
            },
            {
                "ChassisType": "Rack",
                "Name": "Rack 2",
                "Id": "3"
            }
        ]
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
        CONF.set_override('url', 'http://localhost:8442/', group='podm')
        mock_get_url.return_value = '/redfish/v1/Nodes'

        # Fake response for getting nodes root
        fake_node_root_resp = fakes.mock_request_get(fakes.fake_nodes_root(),
                                                     http_client.OK)
        # Fake response for allocating node
        fake_node_allocation_conflict = mock.MagicMock()
        fake_node_allocation_conflict.status_code = http_client.CREATED
        fake_node_allocation_conflict.headers['Location'] = \
            os.path.normpath("/".join([CONF.podm.url, 'redfish/v1/Nodes/1']))

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
        CONF.set_override('url', 'http://localhost:8442/', group='podm')
        mock_get_url.return_value = '/redfish/v1/Nodes'

        # Fake response for getting nodes root
        fake_node_root_resp = fakes.mock_request_get(fakes.fake_nodes_root(),
                                                     http_client.OK)
        # Fake response for allocating node
        fake_node_allocation_conflict = mock.MagicMock()
        fake_node_allocation_conflict.status_code = http_client.CREATED
        fake_node_allocation_conflict.headers['Location'] = \
            os.path.normpath("/".join([CONF.podm.url, 'redfish/v1/Nodes/1']))

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
    def test_reset_node_malformed_request(self, mock_get_url, mock_request):
        """Test reset node with malformed request content"""
        mock_get_url.return_value = '/redfish/v1/Nodes'
        mock_request.return_value = fakes.mock_request_get(
            fakes.fake_node_detail(), http_client.OK)

        with self.assertRaises(exception.BadRequest) as context:
            redfish.reset_node("1", {"fake_request": "fake_value"})

        self.assertTrue("The content of node action request is malformed. "
                        "Please refer to Valence api specification to correct "
                        "it." in str(context.exception.detail))

    @mock.patch('valence.redfish.redfish.send_request')
    @mock.patch('valence.redfish.redfish.get_base_resource_url')
    def test_reset_node_wrong_request(self, mock_get_url, mock_request):
        """Test reset node with wrong action type"""
        mock_get_url.return_value = '/redfish/v1/Nodes'
        mock_request.return_value = fakes.mock_request_get(
            fakes.fake_node_detail(), http_client.OK)

        with self.assertRaises(exception.BadRequest) as context:
            redfish.reset_node("1", {"Reset": {"Type": "wrong_action"}})

        self.assertTrue("Action type 'wrong_action' is not in allowable action"
                        " list" in str(context.exception.detail))

    @mock.patch('valence.redfish.redfish.send_request')
    @mock.patch('valence.redfish.redfish.get_base_resource_url')
    def test_reset_node_success(self, mock_get_url, mock_request):
        """Test successfully reset node status"""
        mock_get_url.return_value = '/redfish/v1/Nodes'
        fake_node_detail = fakes.mock_request_get(
            fakes.fake_node_detail(), http_client.OK)
        fake_node_action_resp = fakes.mock_request_get(
            {}, http_client.NO_CONTENT)
        mock_request.side_effect = [fake_node_detail, fake_node_action_resp]

        result = redfish.reset_node("1", {"Reset": {"Type": "On"}})
        expected = exception.confirmation(
            confirm_code="Reset Composed Node",
            confirm_detail="This composed node has been set to 'On' "
                           "successfully.")

        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.send_request')
    @mock.patch('valence.redfish.redfish.get_base_resource_url')
    def test_set_boot_source_wrong_request(self, mock_get_url, mock_request):
        """Test reset node with wrong action type"""
        mock_get_url.return_value = '/redfish/v1/Nodes'
        mock_request.return_value = fakes.mock_request_get(
            fakes.fake_node_detail(), http_client.OK)

        # Test no "Target" parameter
        with self.assertRaises(exception.BadRequest) as context:
            redfish.set_boot_source("1", {"Boot": {"Enabled": "Once"}})

        self.assertTrue("The content of set boot source request is malformed. "
                        "Please refer to Valence api specification to correct "
                        "it." in str(context.exception.detail))

        # Test no "Enabled" parameter
        with self.assertRaises(exception.BadRequest) as context:
            redfish.set_boot_source("1", {"Boot": {"Target": "Hdd"}})

        self.assertTrue("The content of set boot source request is malformed. "
                        "Please refer to Valence api specification to correct "
                        "it." in str(context.exception.detail))

        # Test no "Enabled" either "Target" parameter
        with self.assertRaises(exception.BadRequest) as context:
            redfish.set_boot_source("1", {"Boot": {}})

        self.assertTrue("The content of set boot source request is malformed. "
                        "Please refer to Valence api specification to correct "
                        "it." in str(context.exception.detail))

        # Test wrong "Enabled" parameter
        with self.assertRaises(exception.BadRequest) as context:
            redfish.set_boot_source("1", {"Boot": {"Enabled": "wrong_input",
                                                   "Target": "Hdd"}})

        self.assertTrue("The parameter Enabled 'wrong_input' is not in "
                        "allowable list ['Disabled', 'Once', 'Continuous']."
                        in str(context.exception.detail))

        # Test wrong "Enabled" parameter
        with self.assertRaises(exception.BadRequest) as context:
            redfish.set_boot_source("1", {"Boot": {"Enabled": "Once",
                                                   "Target": "wrong_input"}})

        allowable_boot_target = \
            (fakes.fake_node_detail()["Boot"]
             ["BootSourceOverrideTarget@Redfish.AllowableValues"])
        self.assertTrue("The parameter Target 'wrong_input' is not in "
                        "allowable list {0}.".format(allowable_boot_target)
                        in str(context.exception.detail))

    @mock.patch('valence.redfish.redfish.send_request')
    @mock.patch('valence.redfish.redfish.get_base_resource_url')
    def test_set_boot_source_success(self, mock_get_url, mock_request):
        """Test successfully reset node status"""
        mock_get_url.return_value = '/redfish/v1/Nodes'
        fake_node_detail = fakes.mock_request_get(
            fakes.fake_node_detail(), http_client.OK)
        fake_node_action_resp = fakes.mock_request_get(
            {}, http_client.NO_CONTENT)
        mock_request.side_effect = [fake_node_detail, fake_node_action_resp]

        result = redfish.set_boot_source(
            "1", {"Boot": {"Enabled": "Once", "Target": "Hdd"}})
        expected = exception.confirmation(
            confirm_code="Set Boot Source of Composed Node",
            confirm_detail="The boot source of composed node has been set to "
                           "'{0}' with enabled state '{1}' successfully."
                           .format("Hdd", "Once"))

        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.reset_node')
    def test_node_action_malformed_request(self, mock_reset_node):
        """Test post node_action with malformed request"""

        # Unsupported multiple action
        with self.assertRaises(exception.BadRequest) as context:
            redfish.node_action(
                "1", {"Reset": {"Type": "On"}, "Assemble": {}})
        self.assertTrue("No action found or multiple actions in one single "
                        "request. Please refer to Valence api specification "
                        "to correct the content of node action request."
                        in str(context.exception.detail))
        mock_reset_node.assert_not_called()

        # Unsupported action
        with self.assertRaises(exception.BadRequest) as context:
            redfish.node_action(
                "1", {"Assemble": {}})
        self.assertTrue("This node action 'Assemble' is unsupported. Please "
                        "refer to Valence api specification to correct this "
                        "content of node action request."
                        in str(context.exception.detail))
        mock_reset_node.assert_not_called()

    @mock.patch('valence.redfish.redfish.reset_node')
    def test_node_action_success(self, mock_reset_node):
        """Test post node_action success"""

        redfish.node_action("1", {"Reset": {"Type": "On"}})

        mock_reset_node.assert_called_once_with("1", {"Reset": {"Type": "On"}})

    @mock.patch('valence.redfish.redfish.get_systems_in_chassis')
    @mock.patch('valence.redfish.redfish.get_base_resource_url')
    @mock.patch('valence.redfish.redfish.filter_chassis')
    @mock.patch('valence.redfish.redfish.send_request')
    def test_list_racks(self, mock_request, mock_filter, mock_base_url,
                        mock_system_list):
        mock_base_url.return_value = "/redfish/v1/Chassis"
        fake_chassis_list = fakes.fake_chassis_list()
        mock_request.return_value = (
            fakes.mock_request_get(fake_chassis_list, "200"))
        mock_filter.return_value = fakes.fake_rack_list()
        mock_system_list.side_effect = [
            [
                "2cd33e50-0e7a-11e7-8c14-c5fab3f6ca28",
                "2a911680-0e7a-11e7-8c14-c5fab3f6ca28",
                "4cadbee1-fe07-11e6-8c14-c5fab3f6ca28"
            ],
            [
                "7ac441b3-a4a1-44f4-8b38-469492cbfb61",
                "3bf332e4-100c-11e7-93ae-92361f002671"
            ]
        ]
        expected = [
            {
                "id": "2",
                "name": "Rack 1",
                "systems": [
                    "2cd33e50-0e7a-11e7-8c14-c5fab3f6ca28",
                    "2a911680-0e7a-11e7-8c14-c5fab3f6ca28",
                    "4cadbee1-fe07-11e6-8c14-c5fab3f6ca28"
                ]
            },
            {
                "id": "3",
                "name": "Rack 2",
                "systems": [
                    "7ac441b3-a4a1-44f4-8b38-469492cbfb61",
                    "3bf332e4-100c-11e7-93ae-92361f002671"
                ]
            }
        ]
        result = redfish.list_racks()
        self.assertEqual(expected, result)

    @mock.patch('valence.redfish.redfish.get_systems_in_chassis')
    @mock.patch('valence.redfish.redfish.get_base_resource_url')
    @mock.patch('valence.redfish.redfish.filter_chassis')
    @mock.patch('valence.redfish.redfish.send_request')
    def test_show_rack(self, mock_request, mock_filter, mock_base_url,
                       mock_system_list):
        mock_base_url.return_value = "/redfish/v1/Chassis"
        fake_chassis_list = fakes.fake_chassis_list()
        mock_request.return_value = (
            fakes.mock_request_get(fake_chassis_list, "200"))
        mock_filter.return_value = fakes.fake_rack_list()
        mock_system_list.return_value = [
            "2cd33e50-0e7a-11e7-8c14-c5fab3f6ca28",
            "2a911680-0e7a-11e7-8c14-c5fab3f6ca28",
            "4cadbee1-fe07-11e6-8c14-c5fab3f6ca28"
        ]
        expected = [
            {
                "description": "Rack created by PODM",
                "id": "2",
                "manufacturer": "Intel",
                "model": "RSD_1",
                "name": "Rack 1",
                "serial_number": "12345",
                "systems": [
                    "2cd33e50-0e7a-11e7-8c14-c5fab3f6ca28",
                    "2a911680-0e7a-11e7-8c14-c5fab3f6ca28",
                    "4cadbee1-fe07-11e6-8c14-c5fab3f6ca28"
                ]
            }
        ]
        result = redfish.show_rack("2")
        self.assertEqual(expected, result)
