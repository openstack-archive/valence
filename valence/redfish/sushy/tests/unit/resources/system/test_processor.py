# All Rights Reserved.
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

import json

import mock

import sushy
from sushy.resources.system import processor
from sushy.tests.unit import base


class ProcessorTestCase(base.TestCase):

    def setUp(self):
        super(ProcessorTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/processor.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.sys_processor = processor.Processor(
            self.conn, '/redfish/v1/Systems/437XR1138R2/Processors/CPU1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.sys_processor._parse_attributes()
        self.assertEqual('1.0.2', self.sys_processor.redfish_version)
        self.assertEqual('CPU1', self.sys_processor.identity)
        self.assertEqual('CPU 1', self.sys_processor.socket)
        self.assertEqual('CPU', self.sys_processor.processor_type)
        self.assertEqual(sushy.PROCESSOR_ARCH_x86,
                         self.sys_processor.processor_architecture)
        self.assertEqual('x86-64', self.sys_processor.instruction_set)
        self.assertEqual('Intel(R) Corporation',
                         self.sys_processor.manufacturer)
        self.assertEqual('Multi-Core Intel(R) Xeon(R) processor 7xxx Series',
                         self.sys_processor.model)
        self.assertEqual(3700, self.sys_processor.max_speed_mhz)
        self.assertEqual(8, self.sys_processor.total_cores)
        self.assertEqual(16, self.sys_processor.total_threads)


class ProcessorCollectionTestCase(base.TestCase):

    def setUp(self):
        super(ProcessorCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'processor_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        self.sys_processor_col = processor.ProcessorCollection(
            self.conn, '/redfish/v1/Systems/437XR1138R2/Processors',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.sys_processor_col._parse_attributes()
        self.assertEqual('1.0.2', self.sys_processor_col.redfish_version)
        self.assertEqual('Processors Collection', self.sys_processor_col.name)
        self.assertEqual(('/redfish/v1/Systems/437XR1138R2/Processors/CPU1',
                          '/redfish/v1/Systems/437XR1138R2/Processors/CPU2'),
                         self.sys_processor_col.members_identities)

    @mock.patch.object(processor, 'Processor', autospec=True)
    def test_get_member(self, mock_processor):
        self.sys_processor_col.get_member(
            '/redfish/v1/Systems/437XR1138R2/Processors/CPU1')
        mock_processor.assert_called_once_with(
            self.sys_processor_col._conn,
            '/redfish/v1/Systems/437XR1138R2/Processors/CPU1',
            redfish_version=self.sys_processor_col.redfish_version)

    @mock.patch.object(processor, 'Processor', autospec=True)
    def test_get_members(self, mock_processor):
        members = self.sys_processor_col.get_members()
        calls = [
            mock.call(self.sys_processor_col._conn,
                      '/redfish/v1/Systems/437XR1138R2/Processors/CPU1',
                      redfish_version=self.sys_processor_col.redfish_version),
            mock.call(self.sys_processor_col._conn,
                      '/redfish/v1/Systems/437XR1138R2/Processors/CPU2',
                      redfish_version=self.sys_processor_col.redfish_version)
        ]
        mock_processor.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(2, len(members))

    def _setUp_processor_summary(self):
        self.conn.get.return_value.json.reset_mock()
        successive_return_values = []
        with open('sushy/tests/unit/json_samples/processor.json', 'r') as f:
            successive_return_values.append(json.loads(f.read()))
        with open('sushy/tests/unit/json_samples/processor2.json', 'r') as f:
            successive_return_values.append(json.loads(f.read()))

        self.conn.get.return_value.json.side_effect = successive_return_values

    def test_summary(self):
        # check for the underneath variable value
        self.assertIsNone(self.sys_processor_col._summary)
        # | GIVEN |
        self._setUp_processor_summary()
        # | WHEN |
        actual_summary = self.sys_processor_col.summary
        # | THEN |
        self.assertEqual((16, sushy.PROCESSOR_ARCH_x86),
                         actual_summary)
        self.assertEqual(16, actual_summary.count)
        self.assertEqual(sushy.PROCESSOR_ARCH_x86,
                         actual_summary.architecture)

        # reset mock
        self.conn.get.return_value.json.reset_mock()

        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_summary,
                      self.sys_processor_col.summary)
        self.conn.get.return_value.json.assert_not_called()

    def test_summary_on_refresh(self):
        # | GIVEN |
        self._setUp_processor_summary()
        # | WHEN & THEN |
        self.assertEqual((16, sushy.PROCESSOR_ARCH_x86),
                         self.sys_processor_col.summary)

        self.conn.get.return_value.json.side_effect = None
        # On refreshing the sys_processor_col instance...
        with open('sushy/tests/unit/json_samples/'
                  'processor_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        self.sys_processor_col.refresh()

        # | WHEN & THEN |
        self.assertIsNone(self.sys_processor_col._summary)

        # | GIVEN |
        self._setUp_processor_summary()
        # | WHEN & THEN |
        self.assertEqual((16, sushy.PROCESSOR_ARCH_x86),
                         self.sys_processor_col.summary)
