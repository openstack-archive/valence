# Copyright (c) 2017 NEC, Corp.
#
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

import copy
import unittest

import mock

from valence.common import exception
from valence.controller import pooled_devices
from valence.podmanagers import podm_base
from valence.tests.unit.db import utils
from valence.tests.unit.fakes import device_fakes as fakes


class TestPooledDevices(unittest.TestCase):

    @mock.patch('valence.db.api.Connection.list_devices')
    def test_list_devices(self, mock_db_list_devices):
        mock_db_list_devices.return_value = fakes.fake_device_model_list()
        result = pooled_devices.PooledDevices.list_devices()
        self.assertEqual(fakes.fake_device_list(), result)

    def test_show_device_brief_info(self):
        device = fakes.fake_device()
        expected = {
            "node_id": None,
            "podm_id": "88888888-8888-8888-8888-888888888888",
            "pooled_group_id": "0000",
            "resource_uri": "devices/0x7777777777",
            "state": "free",
            "type": "NIC",
            "uuid": "00000000-0000-0000-0000-000000000000"
        }
        self.assertEqual(
            expected,
            pooled_devices.PooledDevices._show_device_brief_info(device))

    @mock.patch('valence.controller.pooled_devices.PooledDevices.'
                'update_device_info')
    def test_synchronize_devices_with_podid(self, mock_update_device):
        mock_update_device.return_value = None
        result = pooled_devices.PooledDevices.synchronize_devices('fake_uuid')
        expected = [{'podm_id': 'fake_uuid', 'status': 'SUCCESS'}]
        self.assertEqual(result, expected)

    @mock.patch('valence.controller.pooled_devices.PooledDevices.'
                'update_device_info')
    def test_synchronize_devices_with_fail_update(self, mock_update_device):
        mock_update_device.side_effect = exception.ValenceException
        result = pooled_devices.PooledDevices.synchronize_devices('fake_uuid')
        expected = [{'podm_id': 'fake_uuid', 'status': 'FAILED'}]
        mock_update_device.assert_called_once_with('fake_uuid')
        self.assertEqual(result, expected)

    @mock.patch('valence.db.api.Connection.list_podmanager')
    def test_synchronize_devices_wo_podid(self, mock_pod_db_list):
        mock_pod_db_list.return_value = []
        result = pooled_devices.PooledDevices.synchronize_devices()
        self.assertIsNone(result)

    @mock.patch('valence.controller.pooled_devices.PooledDevices.'
                'update_device_info')
    @mock.patch('valence.db.api.Connection.list_podmanager')
    def test_synchronize_devices_with_db_pods(self, mock_pod_db_list,
                                              mock_update_device):
        podm = utils.get_test_podmanager()
        podm_list = [podm]
        mock_pod_db_list.return_value = podm_list
        mock_update_device.return_value = None
        result = pooled_devices.PooledDevices.synchronize_devices()
        expected = [{'podm_id': podm['uuid'],
                     'status': 'SUCCESS'}]
        mock_update_device.assert_called_once_with(podm['uuid'])
        self.assertEqual(result, expected)

    @mock.patch('valence.controller.pooled_devices.PooledDevices.'
                'update_device_info')
    @mock.patch('valence.db.api.Connection.list_podmanager')
    def test_sync_devices_with_db_pod_and_exception(self,
                                                    mock_pod_list,
                                                    mock_update_device):
        podm = utils.get_test_podmanager()
        podm_list = [podm]
        mock_pod_list.return_value = podm_list
        mock_update_device.side_effect = exception.ValenceException
        result = pooled_devices.PooledDevices.synchronize_devices()
        expected = [{'podm_id': podm['uuid'], 'status': 'FAILED'}]
        mock_update_device.assert_called_once_with(podm['uuid'])
        self.assertEqual(result, expected)

    @mock.patch('valence.podmanagers.podm_base.PodManagerBase.get_all_devices')
    @mock.patch('valence.podmanagers.manager.get_connection')
    @mock.patch('valence.db.api.Connection.list_devices')
    @mock.patch('valence.redfish.sushy.sushy_instance.RedfishInstance')
    def test_update_device_info_wo_change(self, mock_redfish,
                                          mock_device_list,
                                          mock_pod_conn,
                                          mock_get_devices):
        mock_device_list.return_value = fakes.fake_device_list()
        mock_pod_conn.return_value = podm_base.PodManagerBase(
            'fake', 'fake-pass', 'http://fake-url')
        mock_get_devices.return_value = fakes.fake_device_list()
        result = pooled_devices.PooledDevices.update_device_info('fake_id')
        self.assertIsNone(result)

    @mock.patch('valence.db.api.Connection.update_device')
    @mock.patch('valence.podmanagers.podm_base.PodManagerBase.get_all_devices')
    @mock.patch('valence.podmanagers.manager.get_connection')
    @mock.patch('valence.db.api.Connection.list_devices')
    @mock.patch('valence.redfish.sushy.sushy_instance.RedfishInstance')
    def test_update_device_info_with_change(self, mock_redfish,
                                            mock_device_list,
                                            mock_pod_conn,
                                            mock_get_devices,
                                            mock_update_device):
        db_device_list = fakes.fake_device_list()
        connected_devices = copy.deepcopy(db_device_list)
        connected_devices[0]['pooled_group_id'] = '1234'
        connected_devices[0]['node_id'] = '0x1234'
        connected_devices[0]['state'] = 'free'
        mock_device_list.return_value = db_device_list
        mock_pod_conn.return_value = podm_base.PodManagerBase(
            'fake', 'fake-pass', 'http://fake-url')
        mock_get_devices.return_value = connected_devices
        result = pooled_devices.PooledDevices.update_device_info('fake_id')
        values = {'pooled_group_id': '1234',
                  'node_id': '0x1234',
                  'state': 'free'
                  }
        mock_update_device.assert_called_once_with(db_device_list[0]['uuid'],
                                                   values)
        self.assertIsNone(result)

    @mock.patch('valence.db.api.Connection.add_device')
    @mock.patch('valence.podmanagers.podm_base.PodManagerBase.get_all_devices')
    @mock.patch('valence.podmanagers.manager.get_connection')
    @mock.patch('valence.db.api.Connection.list_devices')
    @mock.patch('valence.redfish.sushy.sushy_instance.RedfishInstance')
    def test_update_device_info_with_new_device(self, mock_redfish,
                                                mock_device_list,
                                                mock_pod_conn,
                                                mock_get_devices,
                                                mock_add_device):
        device = fakes.fake_device()
        connected_devices = [device]
        mock_pod_conn.return_value = podm_base.PodManagerBase(
            'fake', 'fake-pass', 'http://fake-url')
        mock_get_devices.return_value = connected_devices
        result = pooled_devices.PooledDevices.update_device_info('fake_id')
        device['podm_id'] = 'fake_id'
        mock_add_device.assert_called_once_with(device)
        self.assertIsNone(result)

    @mock.patch('valence.db.api.Connection.delete_device')
    @mock.patch('valence.db.api.Connection.add_device')
    @mock.patch('valence.podmanagers.podm_base.PodManagerBase.get_all_devices')
    @mock.patch('valence.podmanagers.manager.get_connection')
    @mock.patch('valence.db.api.Connection.list_devices')
    @mock.patch('valence.redfish.sushy.sushy_instance.RedfishInstance')
    def test_update_device_info_with_extra_device_in_db(self, mock_redfish,
                                                        mock_device_list,
                                                        mock_pod_conn,
                                                        mock_get_devices,
                                                        mock_add_device,
                                                        mock_delete_device):
        db_dev_list = fakes.fake_device_list()
        mock_device_list.return_value = db_dev_list
        device = fakes.fake_device()
        connected_devices = [device]
        mock_pod_conn.return_value = podm_base.PodManagerBase(
            'fake', 'fake-pass', 'http://fake-url')
        mock_get_devices.return_value = connected_devices
        result = pooled_devices.PooledDevices.update_device_info('fake_id')
        mock_delete_device.assert_any_call(db_dev_list[0]['uuid'])
        mock_delete_device.assert_any_call(db_dev_list[1]['uuid'])
        self.assertIsNone(result)

    @mock.patch('valence.podmanagers.manager.get_connection')
    @mock.patch('valence.db.api.Connection.list_devices')
    @mock.patch('valence.redfish.sushy.sushy_instance.RedfishInstance')
    def test_update_device_info_with_exception(self, mock_redfish,
                                               mock_device_list,
                                               mock_pod_conn):
        mock_device_list.return_value = [fakes.fake_device()]
        mock_pod_conn.side_effect = exception.ValenceException('fake_detail')
        self.assertRaises(exception.ValenceException,
                          pooled_devices.PooledDevices.update_device_info,
                          'fake_podm_id')
