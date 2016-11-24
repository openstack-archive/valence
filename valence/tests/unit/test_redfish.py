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
from requests.compat import urljoin
from unittest import TestCase

from valence import config as cfg
from valence.redfish import redfish
from valence.tests.unit import fakes


class TestRedfish(TestCase):

    def test_get_rfs_url(self):
        cfg.podm_url = "https://127.0.0.1:8443"
        expected = urljoin(cfg.podm_url, "redfish/v1/Systems/1")

        # test without service_ext
        result = redfish.get_rfs_url("/Systems/1")
        self.assertEqual(expected, result)

        result = redfish.get_rfs_url("Systems/1")
        self.assertEqual(expected, result)

        # test with service_ext
        result = redfish.get_rfs_url("/redfish/v1/Systems/1")
        self.assertEqual(expected, result)

        result = redfish.get_rfs_url("redfish/v1/Systems/1")
        self.assertEqual(expected, result)

    def test_get_rfs_url_with_tailing_slash(self):
        cfg.podm_url = "https://127.0.0.1:8443/"
        expected = urljoin(cfg.podm_url, "redfish/v1/Systems/1")

        # test without service_ext
        result = redfish.get_rfs_url("/Systems/1")
        self.assertEqual(expected, result)

        result = redfish.get_rfs_url("Systems/1")
        self.assertEqual(expected, result)

        # test with service_ext
        result = redfish.get_rfs_url("/redfish/v1/Systems/1")
        self.assertEqual(expected, result)

        result = redfish.get_rfs_url("redfish/v1/Systems/1")
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
        chassis = ('{"Members":'
                   '[{"@odata.id": "1"},'
                   '{"@odata.id": "2"},'
                   '{"@odata.id": "3"}]}')
        expected = {'Members': [
            {u'@odata.id': u'2'},
            {u'@odata.id': u'3'}
        ], 'Members@odata.count': 2}
        result = redfish.filter_chassis(chassis, "Rack")
        self.assertEqual(expected, result)
