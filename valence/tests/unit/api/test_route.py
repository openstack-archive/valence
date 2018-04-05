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

import unittest

import mock

from valence.common import config
config.parse_args = mock.Mock()  # noqa

from valence.api import route


class TestRoute(unittest.TestCase):

    def setUp(self):
        self.app = route.app.test_client()
        self.api = route.api

    def test_app(self):
        self.assertNotEqual(self.app, None)
        self.assertEqual(self.app.__class__.__name__, 'FlaskClient')

    def test_api(self):
        self.assertNotEqual(self.api, None)
        self.assertEqual(self.api.__class__.__name__, 'ValenceService')

        self.assertEqual(self.api.owns_endpoint('v2'), False)

        self.assertEqual(self.api.owns_endpoint('root'), True)
        self.assertEqual(self.api.owns_endpoint('v1'), True)
        self.assertEqual(self.api.owns_endpoint('racks'), True)
        self.assertEqual(self.api.owns_endpoint('nodes'), True)
        self.assertEqual(self.api.owns_endpoint('node'), True)
        self.assertEqual(self.api.owns_endpoint('nodes_storages'), True)
        self.assertEqual(self.api.owns_endpoint('node_register'), True)
        self.assertEqual(self.api.owns_endpoint('systems'), True)
        self.assertEqual(self.api.owns_endpoint('system'), True)
        self.assertEqual(self.api.owns_endpoint('flavors'), True)
        self.assertEqual(self.api.owns_endpoint('flavor'), True)
        self.assertEqual(self.api.owns_endpoint('storages'), True)
        self.assertEqual(self.api.owns_endpoint('storage'), True)
        self.assertEqual(self.api.owns_endpoint('devices'), True)
        self.assertEqual(self.api.owns_endpoint('device'), True)
        self.assertEqual(self.api.owns_endpoint('sync'), True)
        self.assertEqual(self.api.owns_endpoint('podmproxy'), True)
