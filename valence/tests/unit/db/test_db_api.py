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
import unittest

import etcd
import freezegun
import mock

from valence.common import exception
from valence.db import api as db_api
from valence.tests.unit.db import utils


class TestDBAPI(unittest.TestCase):

    @freezegun.freeze_time("2017-01-01")
    @mock.patch('etcd.Client.write')
    @mock.patch('etcd.Client.read')
    def test_create_podmanager(self, mock_etcd_read, mock_etcd_write):
        podmanager = utils.get_test_podmanager()
        fake_utcnow = '2017-01-01 00:00:00 UTC'
        podmanager['created_at'] = fake_utcnow
        podmanager['updated_at'] = fake_utcnow

        # Mark this uuid don't exist in etcd db
        mock_etcd_read.side_effect = etcd.EtcdKeyNotFound

        result = db_api.Connection.create_podmanager(podmanager)
        self.assertEqual(podmanager, result.as_dict())
        mock_etcd_read.assert_called_with(
            '/pod_managers/' + podmanager['uuid'])
        mock_etcd_write.assert_called_with(
            '/pod_managers/' + podmanager['uuid'],
            json.dumps(result.as_dict()))

    @freezegun.freeze_time('2017-01-01')
    @mock.patch('etcd.Client.write')
    @mock.patch('etcd.Client.read')
    def test_create_flavor(self, mock_etcd_read, mock_etcd_write):
        flavor = utils.get_test_flavor()
        fake_utcnow = '2017-01-01 00:00:00 UTC'
        flavor['created_at'] = fake_utcnow
        flavor['updated_at'] = fake_utcnow

        mock_etcd_read.side_effect = etcd.EtcdKeyNotFound

        result = db_api.Connection.create_flavor(flavor)
        self.assertEqual(flavor, result.as_dict())
        mock_etcd_read.assert_called_with('/flavors/' + flavor['uuid'])
        mock_etcd_write.assert_called_with('/flavors/' + flavor['uuid'],
                                           json.dumps(result.as_dict()))

    @mock.patch('etcd.Client.read')
    def test_get_podmanager_by_uuid(self, mock_etcd_read):
        podmanager = utils.get_test_podmanager()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            podmanager['uuid'], json.dumps(podmanager))
        result = db_api.Connection.get_podmanager_by_uuid(podmanager['uuid'])

        self.assertEqual(podmanager, result.as_dict())
        mock_etcd_read.assert_called_with(
            '/pod_managers/' + podmanager['uuid'])

    @mock.patch('etcd.Client.read')
    def test_get_flavor_by_uuid(self, mock_etcd_read):
        flavor = utils.get_test_flavor()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            flavor['uuid'], json.dumps(flavor))
        result = db_api.Connection.get_flavor_by_uuid(flavor['uuid'])

        self.assertEqual(flavor, result.as_dict())
        mock_etcd_read.assert_called_with(
            '/flavors/' + flavor['uuid'])

    @mock.patch('etcd.Client.read')
    def test_get_podmanager_not_found(self, mock_etcd_read):
        podmanager = utils.get_test_podmanager()
        mock_etcd_read.side_effect = etcd.EtcdKeyNotFound

        with self.assertRaises(Exception) as context:  # noqa: H202
            db_api.Connection.get_podmanager_by_uuid(podmanager['uuid'])

        self.assertTrue('Pod manager not found {0} in database.'.format(
            podmanager['uuid']) in str(context.exception))
        mock_etcd_read.assert_called_with(
            '/pod_managers/' + podmanager['uuid'])

    @mock.patch('etcd.Client.read')
    def test_get_flavor_not_found(self, mock_etcd_read):
        flavor = utils.get_test_flavor()
        mock_etcd_read.side_effect = etcd.EtcdKeyNotFound

        with self.assertRaises(Exception) as context:  # noqa: H202
            db_api.Connection.get_flavor_by_uuid(flavor['uuid'])

        self.assertTrue('Flavor {0} not found.'.format(
            flavor['uuid']) in str(context.exception))
        mock_etcd_read.assert_called_with('/flavors/' + flavor['uuid'])

    @mock.patch('etcd.Client.delete')
    @mock.patch('etcd.Client.read')
    def test_delete_podmanager(self, mock_etcd_read, mock_etcd_delete):
        podmanager = utils.get_test_podmanager()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            podmanager['uuid'], json.dumps(podmanager))
        db_api.Connection.delete_podmanager(podmanager['uuid'])

        mock_etcd_delete.assert_called_with(
            '/pod_managers/' + podmanager['uuid'])

    @mock.patch('etcd.Client.delete')
    @mock.patch('etcd.Client.read')
    def test_delete_flavor(self, mock_etcd_read, mock_etcd_delete):
        flavor = utils.get_test_flavor()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            flavor['uuid'], json.dumps(flavor))
        db_api.Connection.delete_flavor(flavor['uuid'])

        mock_etcd_delete.assert_called_with('/flavors/' + flavor['uuid'])

    @freezegun.freeze_time("2017-01-01")
    @mock.patch('etcd.Client.write')
    @mock.patch('etcd.Client.read')
    def test_update_podmanager(self, mock_etcd_read, mock_etcd_write):
        podmanager = utils.get_test_podmanager()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            podmanager['uuid'], json.dumps(podmanager))

        fake_utcnow = '2017-01-01 00:00:00 UTC'
        podmanager['updated_at'] = fake_utcnow
        podmanager.update({'url': 'new_url'})

        result = db_api.Connection.update_podmanager(
            podmanager['uuid'], {'url': 'new_url'})

        self.assertEqual(podmanager, result.as_dict())
        mock_etcd_read.assert_called_with(
            '/pod_managers/' + podmanager['uuid'])
        mock_etcd_write.assert_called_with(
            '/pod_managers/' + podmanager['uuid'],
            json.dumps(result.as_dict()))

    @freezegun.freeze_time("2017-01-01")
    @mock.patch('etcd.Client.write')
    @mock.patch('etcd.Client.read')
    def test_update_flavor(self, mock_etcd_read, mock_etcd_write):
        flavor = utils.get_test_flavor()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            flavor['uuid'], json.dumps(flavor))

        fake_utcnow = '2017-01-01 00:00:00 UTC'
        flavor['updated_at'] = fake_utcnow
        flavor.update({'properties': {'memory': {'type': 'new_type'}}})

        result = db_api.Connection.update_flavor(
            flavor['uuid'], {'properties': {'memory': {'type': 'new_type'}}})

        self.assertEqual(flavor, result.as_dict())
        mock_etcd_read.assert_called_with(
            '/flavors/' + flavor['uuid'])
        mock_etcd_write.assert_called_with(
            '/flavors/' + flavor['uuid'],
            json.dumps(result.as_dict()))

    @freezegun.freeze_time("2017-01-01")
    @mock.patch('etcd.Client.write')
    @mock.patch('etcd.Client.read')
    def test_create_podm_resource(self, mock_etcd_read, mock_etcd_write):
        resource = utils.get_test_podm_resource()
        fake_utcnow = '2017-01-01 00:00:00 UTC'
        resource['created_at'] = fake_utcnow
        resource['updated_at'] = fake_utcnow

        # Mark this uuid don't exist in etcd db
        mock_etcd_read.side_effect = etcd.EtcdKeyNotFound

        result = db_api.Connection.create_podm_resource(resource)
        self.assertEqual(resource, result.as_dict())
        mock_etcd_read.assert_called_once_with(
            '/resources/' + resource['uuid'])
        mock_etcd_write.assert_called_once_with(
            '/resources/' + resource['uuid'],
            json.dumps(result.as_dict()))

    @mock.patch('etcd.Client.read')
    def test_get_podm_resource_by_uuid(self, mock_etcd_read):
        resource = utils.get_test_podm_resource()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            resource['uuid'], json.dumps(resource))
        result = db_api.Connection.get_podm_resource_by_uuid(resource['uuid'])

        self.assertEqual(resource, result.as_dict())
        mock_etcd_read.assert_called_once_with(
            '/resources/' + resource['uuid'])

    @mock.patch('etcd.Client.read')
    def test_get_podm_resource_not_found(self, mock_etcd_read):
        resource = utils.get_test_podm_resource()
        mock_etcd_read.side_effect = etcd.EtcdKeyNotFound

        with self.assertRaises(exception.NotFound) as context:  # noqa: H202
            db_api.Connection.get_podm_resource_by_uuid(resource['uuid'])

        self.assertTrue(
            'Pod Manager Resource {0} not found in database.'.format(
                resource['uuid']) in str(context.exception.detail))
        mock_etcd_read.assert_called_once_with(
            '/resources/' + resource['uuid'])

    @mock.patch('etcd.Client.delete')
    @mock.patch('etcd.Client.read')
    def test_delete_podm_resource(self, mock_etcd_read, mock_etcd_delete):
        resource = utils.get_test_podm_resource()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            resource['uuid'], json.dumps(resource))
        db_api.Connection.delete_podm_resource(resource['uuid'])

        mock_etcd_delete.assert_called_with(
            '/resources/' + resource['uuid'])

    @freezegun.freeze_time("2017-01-01")
    @mock.patch('etcd.Client.write')
    @mock.patch('etcd.Client.read')
    def test_update_podm_resource(self, mock_etcd_read, mock_etcd_write):
        resource = utils.get_test_podm_resource()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            resource['uuid'], json.dumps(resource))

        fake_utcnow = '2017-01-01 00:00:00 UTC'
        resource['updated_at'] = fake_utcnow
        resource.update({'resource_url': '/redfish/v1/Nodes/2'})

        result = db_api.Connection.update_podm_resource(
            resource['uuid'], {'resource_url': '/redfish/v1/Nodes/2'})

        self.assertEqual(resource, result.as_dict())
        mock_etcd_read.assert_called_with(
            '/resources/' + resource['uuid'])
        mock_etcd_write.assert_called_with(
            '/resources/' + resource['uuid'],
            json.dumps(result.as_dict()))
