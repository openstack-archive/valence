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

import unittest

import mock

from ironicclient import client as ironicclient

from valence.common import clients
import valence.conf


class ClientsTest(unittest.TestCase):

    def setUp(self):
        super(ClientsTest, self).setUp()

        valence.conf.CONF.set_override('auth_url',
                                       'http://server.test:5000/v2.0',
                                       group='ironic_client')
        valence.conf.CONF.set_override('api_version', 1,
                                       group='ironic_client')

    @mock.patch.object(ironicclient, 'get_client')
    def test_clients_ironic(self, mock_client):
        obj = clients.OpenStackClients()
        obj._ironic = None
        obj.ironic()
        mock_client.assert_called_once_with(
            valence.conf.CONF.ironic_client.api_version,
            os_auth_url='http://server.test:5000/v2.0', os_username=None,
            os_project_name=None,
            os_project_domain_id=None,
            os_user_domain_id=None,
            os_password=None, os_cacert=None, os_cert=None,
            os_key=None, insecure=False)

    @mock.patch.object(ironicclient, 'get_client')
    def test_clients_ironic_cached(self, mock_client):
        obj = clients.OpenStackClients()
        obj._ironic = None
        ironic = obj.ironic()
        ironic_cached = obj.ironic()
        self.assertEqual(ironic, ironic_cached)
