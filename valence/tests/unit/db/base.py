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

from etcd.tests import unit as etcd_test

from valence.db import etcd_api


class TestDBBase(etcd_test.TestClientApiBase):

    def setUp(self):
        super(TestDBBase, self).setUp()
        etcd_api.get_driver().client = self.client

    def _mock_etcd_read(self, key, value):
        data = {
            u'action': u'get',
            u'node': {
                u'modifiedIndex': 190,
                u'key': key,
                u'value': value
                }
            }

        self._mock_api(200, data)

    def _mock_etcd_write(self, key, value):
        data = {
            u'action': u'set',
            u'node': {
                u'expiration': u'2013-09-14T00:56:59.316195568+02:00',
                u'modifiedIndex': 183,
                u'key': key,
                u'ttl': 19,
                u'value': value
            }
        }
        self._mock_api(201, data)
