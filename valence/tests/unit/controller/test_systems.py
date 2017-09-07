# copyright (c) 2017 NEC, Corp.
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

import unittest

import mock

from valence.controller import systems
from valence.podmanagers import podm_base


class TestAPISystems(unittest.TestCase):

    @mock.patch('valence.podmanagers.manager.get_connection')
    @mock.patch('valence.redfish.sushy.sushy_instance.RedfishInstance')
    def setUp(self, mock_redfish, mock_connection):
        self.system_controller = systems.System(podm_id='test-podm-1')
        self.system_controller.connection = podm_base.PodManagerBase(
            'fake', 'fake-pass', 'http://fake-url')

    @mock.patch("valence.podmanagers.podm_base.PodManagerBase.systems_list")
    def test_system_list(self, mock_redfish):
        response = [{
            'uuid': 'fake_system_uuid',
            'name': 'fake-system-name',
            'power_state': 'on',
            'links': 'system/1'
        }]
        mock_redfish.return_value = response
        result = self.system_controller.list_systems()
        self.assertEqual(response, result)
        mock_redfish.assert_called_once_with({})

    @mock.patch.object(podm_base.PodManagerBase, "get_system_by_id")
    def test_get_system_by_id(self, mock_redfish):

        response = {
            'uuid': 'fake_system_id',
            'name': 'fake-system-name',
            'power_state': 'on',
            'health': 'ok',
            'chassis_id': 'c-id',
            'links': 'system/1'
        }
        mock_redfish.return_value = response
        result = self.system_controller.get_system_by_id('fake_system_id')
        mock_redfish.assert_called_once_with('fake_system_id')
        self.assertEqual(response, result)
