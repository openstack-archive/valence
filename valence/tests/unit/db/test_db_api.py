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

import json
import mock
import unittest

import etcd
import freezegun

from valence.db import api as db_api
from valence.tests.unit.db import utils


class TestDBAPI(unittest.TestCase):

    @freezegun.freeze_time("2017-01-01")
    @mock.patch('etcd.Client.write')
    @mock.patch('etcd.Client.read')
    def test_create_podmanager(self, mock_etcd_read, mock_etcd_write):
        podmanager = utils.get_test_image()
        fake_utcnow = '2017-01-01 00:00:00 UTC'
        podmanager['created_at'] = fake_utcnow
        podmanager['updated_at'] = fake_utcnow

        # Mark this uuid don't exist in etcd db
        mock_etcd_read.side_effect = etcd.EtcdKeyNotFound

        result = db_api.Connection.create_podmanager(podmanager)
        self.assertEqual(podmanager, result.as_dict())

    @mock.patch('etcd.Client.read')
    def test_get_podmanager_by_uuid(self, mock_etcd_read):
        podmanager = utils.get_test_image()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            podmanager['uuid'], json.dumps(podmanager))
        result = db_api.Connection.get_podmanager_by_uuid(podmanager['uuid'])

        self.assertEqual(podmanager, result.as_dict())

    @mock.patch('etcd.Client.delete')
    @mock.patch('etcd.Client.read')
    def test_delete_podmanager(self, mock_etcd_read, mock_etcd_delete):
        podmanager = utils.get_test_image()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            podmanager['uuid'], json.dumps(podmanager))
        db_api.Connection.delete_podmanager(podmanager['uuid'])

        mock_etcd_delete.assert_called_with(
            '/pod_managers/' + podmanager['uuid'])

    @freezegun.freeze_time("2017-01-01")
    @mock.patch('etcd.Client.write')
    @mock.patch('etcd.Client.read')
    def test_update_podmanager(self, mock_etcd_read, mock_etcd_write):
        podmanager = utils.get_test_image()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            podmanager['uuid'], json.dumps(podmanager))

        fake_utcnow = '2017-01-01 00:00:00 UTC'
        podmanager['updated_at'] = fake_utcnow
        podmanager.update({'url': 'new_url'})

        result = db_api.Connection.update_podmanager(
            podmanager['uuid'], {'url': 'new_url'})

        self.assertEqual(podmanager, result.as_dict())
