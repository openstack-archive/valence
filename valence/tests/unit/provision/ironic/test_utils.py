# copyright (c) 2017 Intel, Inc.
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

import mock

from oslotest import base

from valence.common import exception
from valence.provision.ironic import utils


class TestUtils(base.BaseTestCase):
    def setUp(self):
        super(TestUtils, self).setUp()

    @mock.patch('valence.common.clients.OpenStackClients.ironic')
    def test_create_ironicclient(self, mock_ironic):
        ironic = utils.create_ironicclient()
        self.assertTrue(ironic)
        mock_ironic.assert_called_once_with()

    @mock.patch('valence.common.clients.OpenStackClients.ironic')
    def test_create_ironic_client_failure(self, mock_client):
        mock_client.side_effect = Exception()
        self.assertRaises(exception.ValenceException,
                          utils.create_ironicclient)
