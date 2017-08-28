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

        with self.assertRaises(exception.NotFound) as context:  # noqa: H202
            db_api.Connection.get_podmanager_by_uuid(podmanager['uuid'])

        self.assertTrue('Pod Manager {0} not found in database.'.format(
            podmanager['uuid']) in str(context.exception))
        mock_etcd_read.assert_called_with(
            '/pod_managers/' + podmanager['uuid'])

    @mock.patch('etcd.Client.read')
    def test_get_flavor_not_found(self, mock_etcd_read):
        flavor = utils.get_test_flavor()
        mock_etcd_read.side_effect = etcd.EtcdKeyNotFound

        with self.assertRaises(exception.NotFound) as context:  # noqa: H202
            db_api.Connection.get_flavor_by_uuid(flavor['uuid'])

        self.assertTrue('Flavor {0} not found in database.'.format(
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
    def test_create_composed_node(self, mock_etcd_read, mock_etcd_write):
        node = utils.get_test_composed_node_db_info()
        fake_utcnow = '2017-01-01 00:00:00 UTC'
        node['created_at'] = fake_utcnow
        node['updated_at'] = fake_utcnow

        # Mark this uuid don't exist in etcd db
        mock_etcd_read.side_effect = etcd.EtcdKeyNotFound

        result = db_api.Connection.create_composed_node(node)
        self.assertEqual(node, result.as_dict())
        mock_etcd_read.assert_called_once_with(
            '/nodes/' + node['uuid'])
        mock_etcd_write.assert_called_once_with(
            '/nodes/' + node['uuid'],
            json.dumps(result.as_dict()))

    @mock.patch('etcd.Client.read')
    def test_get_composed_node_by_uuid(self, mock_etcd_read):
        node = utils.get_test_composed_node_db_info()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            node['uuid'], json.dumps(node))
        result = db_api.Connection.get_composed_node_by_uuid(node['uuid'])

        self.assertEqual(node, result.as_dict())
        mock_etcd_read.assert_called_once_with(
            '/nodes/' + node['uuid'])

    @mock.patch('etcd.Client.read')
    def test_get_composed_node_not_found(self, mock_etcd_read):
        node = utils.get_test_composed_node_db_info()
        mock_etcd_read.side_effect = etcd.EtcdKeyNotFound

        with self.assertRaises(exception.NotFound) as context:  # noqa: H202
            db_api.Connection.get_composed_node_by_uuid(node['uuid'])

        self.assertTrue("Composed node '{0}' not found in database.".format(
            node['uuid']) in str(context.exception))
        mock_etcd_read.assert_called_once_with(
            '/nodes/' + node['uuid'])

    @mock.patch('etcd.Client.delete')
    @mock.patch('etcd.Client.read')
    def test_delete_composed_node(self, mock_etcd_read, mock_etcd_delete):
        node = utils.get_test_composed_node_db_info()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            node['uuid'], json.dumps(node))
        db_api.Connection.delete_composed_node(node['uuid'])

        mock_etcd_delete.assert_called_with(
            '/nodes/' + node['uuid'])

    @freezegun.freeze_time("2017-01-01")
    @mock.patch('etcd.Client.write')
    @mock.patch('etcd.Client.read')
    def test_update_composed_node(self, mock_etcd_read, mock_etcd_write):
        node = utils.get_test_composed_node_db_info()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            node['uuid'], json.dumps(node))

        fake_utcnow = '2017-01-01 00:00:00 UTC'
        node['updated_at'] = fake_utcnow
        node.update({'index': '2'})

        result = db_api.Connection.update_composed_node(
            node['uuid'], {'index': '2'})

        self.assertEqual(node, result.as_dict())
        mock_etcd_read.assert_called_with(
            '/nodes/' + node['uuid'])
        mock_etcd_write.assert_called_with(
            '/nodes/' + node['uuid'],
            json.dumps(result.as_dict()))

    @mock.patch('etcd.Client.read')
    def test_get_device_by_uuid(self, mock_etcd_read):
        device = utils.get_test_device_db_info()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            device['uuid'], json.dumps(device))
        result = db_api.Connection.get_device_by_uuid(device['uuid'])

        self.assertEqual(device, result.as_dict())
        mock_etcd_read.assert_called_once_with(
            '/devices/' + device['uuid'])

    @mock.patch('etcd.Client.read')
    def test_get_device_not_found(self, mock_etcd_read):
        device = utils.get_test_device_db_info()
        mock_etcd_read.side_effect = etcd.EtcdKeyNotFound

        with self.assertRaises(exception.NotFound) as context:
            db_api.Connection.get_device_by_uuid(device['uuid'])

        self.assertTrue('Device {0} not found in database.'.format(
            device['uuid']) in str(context.exception))
        mock_etcd_read.assert_called_with(
            '/devices/' + device['uuid'])

    @mock.patch('etcd.Client.delete')
    @mock.patch('etcd.Client.read')
    def test_delete_device(self, mock_etcd_read, mock_etcd_delete):
        device = utils.get_test_device_db_info()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            device['uuid'], json.dumps(device))
        db_api.Connection.delete_device(device['uuid'])

        mock_etcd_delete.assert_called_with(
            '/devices/' + device['uuid'])

    @freezegun.freeze_time("2017-01-01")
    @mock.patch('etcd.Client.write')
    @mock.patch('etcd.Client.read')
    def test_update_device(self, mock_etcd_read, mock_etcd_write):
        device = utils.get_test_device_db_info()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            device['uuid'], json.dumps(device))

        fake_utcnow = '2017-01-01 00:00:00 UTC'
        device['updated_at'] = fake_utcnow
        device.update({'resource_uri': 'new_uri'})

        result = db_api.Connection.update_device(
            device['uuid'], {'resource_uri': 'new_uri'})

        self.assertEqual(device, result.as_dict())
        mock_etcd_read.assert_called_with(
            '/devices/' + device['uuid'])
        mock_etcd_write.assert_called_with(
            '/devices/' + device['uuid'],
            json.dumps(result.as_dict()))

    @freezegun.freeze_time("2017-01-01")
    @mock.patch('etcd.Client.write')
    @mock.patch('etcd.Client.read')
    def test_create_device(self, mock_etcd_read, mock_etcd_write):
        device = utils.get_test_device_db_info()
        fake_utcnow = '2017-01-01 00:00:00 UTC'
        device['created_at'] = fake_utcnow
        device['updated_at'] = fake_utcnow

        # Mark this uuid don't exist in etcd db
        mock_etcd_read.side_effect = etcd.EtcdKeyNotFound

        result = db_api.Connection.create_device(device)
        self.assertEqual(device, result.as_dict())
        mock_etcd_read.assert_called_once_with(
            '/devices/' + device['uuid'])
        mock_etcd_write.assert_called_once_with(
            '/devices/' + device['uuid'],
            json.dumps(result.as_dict()))

    @mock.patch('etcd.Client.read')
    def test_get_device_list(self, mock_etcd_read):
        device = utils.get_test_device_db_info()

        mock_etcd_read.return_value = utils.get_etcd_read_result(
            None, json.dumps(device))
        result = db_api.Connection.list_devices()
        result = [dev.as_dict() for dev in result]
        self.assertEqual([device], result)
        mock_etcd_read.assert_called_once_with('/devices')
