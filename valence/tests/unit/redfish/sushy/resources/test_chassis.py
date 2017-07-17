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

import json

import mock

from sushy.tests.unit import base

from valence.redfish.sushy.resources import chassis


class TestChassis(base.TestCase):

    def setUp(self):
        super(TestChassis, self).setUp()
        self.conn = mock.Mock()

        with open('valence/tests/unit/redfish/sushy/json_samples/chassis.json',
                  'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.chassis_inst = chassis.Chassis(self.conn,
                                            '/redfish/v1/Chassis/chassis1',
                                            redfish_version='1.0.2')

    def test_parse_attributes(self):
        self.chassis_inst._parse_attributes()
        self.assertEqual('1.0.2', self.chassis_inst.redfish_version)
        self.assertEqual('FlexChassis1', self.chassis_inst.asset_tag)
        self.assertEqual('Drawer', self.chassis_inst.chassis_type)
        self.assertEqual('this is a chassis', self.chassis_inst.description)
        self.assertEqual('Chassis1', self.chassis_inst.identity)
        self.assertEqual('Intel Corporaion', self.chassis_inst.manufacturer)
        self.assertEqual('FLEX-1', self.chassis_inst.name)
        self.assertEqual('5c72-36d6', self.chassis_inst.part_number)
        self.assertEqual('a78255edab51', self.chassis_inst.serial_number)
        self.assertEqual('e1c2d764-5c72', self.chassis_inst.sku)
        self.assertEqual('e1c2d764-5c72-36d6-9945-a78255edab51',
                         self.chassis_inst.oem['Intel:RackScale']['UUID'])


class TestChassisCollection(base.TestCase):

    def setUp(self):
        super(TestChassisCollection, self).setUp()
        self.conn = mock.Mock()

        with open('valence/tests/unit/redfish/sushy/json_samples/'
                  'chassis_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.chassis_col = chassis.ChassisCollection(self.conn,
                                                     '/redfish/v1/Systems',
                                                     redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.chassis_col._parse_attributes()
        self.assertEqual('1.0.2', self.chassis_col.redfish_version)
        self.assertEqual('Chassis Collection', self.chassis_col.name)
        self.assertIn('/redfish/v1/Chassis/Chassis1',
                      self.chassis_col.members_identities)

    @mock.patch.object(chassis, 'Chassis', autospec=True)
    def test_get_member(self, mock_chassis):
        self.chassis_col.get_member('/redfish/v1/Chassis/Chassis1')

        mock_chassis.assert_called_once_with(
            self.chassis_col._conn,
            '/redfish/v1/Chassis/Chassis1',
            redfish_version=self.chassis_col.redfish_version
        )

    @mock.patch.object(chassis, 'Chassis', autospec=True)
    def test_get_members(self, mock_chassis):
        members = self.chassis_col.get_members()
        self.assertEqual(mock_chassis.call_count, 8)
        self.assertIsInstance(members, list)
        self.assertEqual(8, len(members))
