# Copyright 2017 NEC, Corp.
#
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

import mock

from oslotest import base

from valence.common import exception
from valence.podmanagers import manager
from valence.podmanagers import podm_base
from valence.tests.unit.fakes import podmanager_fakes


class TestManager(base.BaseTestCase):
    def setUp(self):
        super(TestManager, self).setUp()

    def test_load_podm_failure(self):
        self.assertRaises(exception.DriverNotFound, manager.Manager.load_podm,
                          'UnknownDriver')

    def test_load_podm(self):
        podm = manager.Manager.load_podm('redfishv1')
        self.assertEqual(manager.podm_modules['redfishv1'], podm)

    @mock.patch("valence.redfish.sushy.sushy_instance.RedfishInstance")
    def test_get_podm_instance(self, mock_redfish):
        mng = manager.Manager('http://fake-url', 'fake-user', 'fake-pass')
        self.assertTrue(isinstance(mng.podm, podm_base.PodManagerBase))

    @mock.patch("valence.db.api.Connection.get_podmanager_by_uuid")
    @mock.patch("valence.redfish.sushy.sushy_instance.RedfishInstance")
    def test_get_podm_connection(self, redfish_mock, get_podm_mock):
        get_podm_mock.return_value = podmanager_fakes.fake_podm_object()
        inst = manager.get_connection("fake-id")
        self.assertTrue(isinstance(inst, podm_base.PodManagerBase))
        self.assertTrue(manager.podm_connections['fake-id'])
