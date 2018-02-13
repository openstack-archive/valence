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

from unittest import TestCase

import mock

from valence.controller import pooled_devices
from valence.tests.unit.fakes import device_fakes as fakes


class TestPooledDevices(TestCase):

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
        self.assertEqual(expected,
                         pooled_devices.PooledDevices._show_device_brief_info(
                             device))
