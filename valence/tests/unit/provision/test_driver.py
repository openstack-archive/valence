# Copyright 2017 Intel.
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
import valence.conf
from valence.provision import driver

CONF = valence.conf.CONF


class TestDriver(base.BaseTestCase):
    def setUp(self):
        super(TestDriver, self).setUp()

    def test_load_driver_failure(self):
        self.assertRaises(exception.ValenceException, driver.load_driver,
                          'UnknownDriver')

    def test_load_driver(self):
        self.assertTrue(driver.load_driver, 'ironic.IronicDriver')

    @mock.patch("valence.provision.driver.load_driver")
    def test_node_register(self, mock_driver):
        driver.node_register('fake-uuid', {})
        mock_driver.assert_called_once()
