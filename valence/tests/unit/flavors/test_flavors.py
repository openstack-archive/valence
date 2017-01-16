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

import mock
import unittest

from valence.flavors import flavors
from valence.tests.unit.fakes import flavors_fakes as fakes


class TestFlavors(unittest.TestCase):

    def test_get_available_criteria(self):
        expected = {'criteria': [{'name': 'default',
                                  'description': 'Generates 3 flavors(Tiny, '
                                                 'Medium, Large) for each '
                                                 'node considering all cpu '
                                                 'cores, ram and storage'},
                                 {'name': 'assettag',
                                  'description': 'Demo only: Generates '
                                                 'location based on assettag'},
                                 {'name': 'example',
                                  'description': 'Description of plugins'}]}
        result = flavors.get_available_criteria()
        expected = sorted(expected['criteria'], key=lambda x: x['name'])
        result = sorted(result['criteria'], key=lambda x: x['name'])
        self.assertEqual(expected, result)

    @mock.patch(
        'valence.flavors.plugins.assettag.assettagGenerator.generate')
    @mock.patch('uuid.uuid4')
    @mock.patch('valence.redfish.redfish.systems_list')
    def test_create_flavors_asserttag(self, mock_systems,
                                      mock_uuid,
                                      mock_generate):
        fake_systems = fakes.fake_flavor_nodes()
        mock_systems.return_value = fake_systems
        mock_uuid.return_value = 'f0f96c58-d3d0-4292-a191'
        mock_generate.return_value = fakes.fake_assettag_flavors()
        result = flavors.create_flavors(data={"criteria": "assettag"})
        expected = [fakes.fake_assettag_flavors()]
        self.assertEqual(expected, result)

    @mock.patch(
        'valence.flavors.plugins.default.defaultGenerator.generate')
    @mock.patch('uuid.uuid4')
    @mock.patch('valence.redfish.redfish.systems_list')
    def test_create_flavors_default(self, mock_systems,
                                    mock_uuid,
                                    mock_generate):
        fake_systems = fakes.fake_flavor_nodes()
        mock_systems.return_value = fake_systems
        mock_uuid.return_value = 'f0f96c58-d3d0-4292-a191'
        mock_generate.return_value = fakes.fake_default_flavors()
        result = flavors.create_flavors(data={"criteria": "default"})
        expected = [fakes.fake_default_flavors()]
        self.assertEqual(expected, result)

    @mock.patch(
        'valence.flavors.plugins.default.defaultGenerator.generate')
    @mock.patch(
        'valence.flavors.plugins.assettag.assettagGenerator.generate')
    @mock.patch('uuid.uuid4')
    @mock.patch('valence.redfish.redfish.systems_list')
    def test_create_flavors_asserttag_and_default(self, mock_systems,
                                                  mock_uuid,
                                                  mock_assettag_generate,
                                                  mock_default_generate):
        fake_systems = fakes.fake_flavor_nodes()
        mock_systems.return_value = fake_systems
        mock_uuid.return_value = 'f0f96c58-d3d0-4292-a191'
        mock_assettag_generate.return_value = \
            fakes.fake_assettag_flavors()
        mock_default_generate.return_value = \
            fakes.fake_default_flavors()
        result = flavors.create_flavors(
            data={"criteria": "assettag,default"})
        expected = [fakes.fake_assettag_flavors(),
                    fakes.fake_default_flavors()]
        self.assertEqual(expected, result)
