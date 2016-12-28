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
from unittest import TestCase
from valence.flavors import flavors


class TestFlavors(TestCase):

    def test_get_available_criteria(self):
        expected = {'criteria': [{'name': 'default',
                                  'description': 'Generates 3 flavors(Tiny, Medium, Large) '
                                                 'for each node considering all cpu cores, '
                                                 'ram and storage'},
                                 {'name': 'assettag', 'description': 'Demo only: Generates '
                                                                     'location based on assettag'},
                                 {'name': 'example', 'description': 'Description of plugins'}]}
        result = flavors.get_available_criteria()
        self.assertEqual(expected, result)

    @mock.patch('uuid.uuid4')
    @mock.patch('valence.redfish.redfish.systems_list')
    def test_create_flavors_asserttag(self, mock_systems, mock_uuid):
        fake_systems = self._make_fake_nodes()
        mock_systems.return_value = fake_systems
        mock_uuid.return_value = 'f0f96c58-d3d0-4292-a191-107e62e340c9'
        result = flavors.create_flavors(data={"criteria": "assettag"})
        expected = [
            [{"flavor":
                  {"name": 'L_irsd-location2',
                   "ram": 2048,
                   "vcpus": 4,
                   "disk": 500,
                   "id": 'f0f96c58-d3d0-4292-a191-107e62e340c9'}},
             {"extra_specs": {'location': '2'}}
             ],
            [{"flavor":
                  {"name": 'M_irsd-location2',
                   "ram": 2048,
                   "vcpus": 4,
                   "disk": 500,
                   "id": 'f0f96c58-d3d0-4292-a191-107e62e340c9'}},
             {"extra_specs": {'location': '2'}}
             ],
            [{"flavor":
                  {"name": 'S_irsd-location2',
                   "ram": 2048,
                   "vcpus": 4,
                   "disk": 500,
                   "id": 'f0f96c58-d3d0-4292-a191-107e62e340c9'}},
             {"extra_specs": {"location": "2"}}
             ]
        ]
        self.assertEqual(expected, result)

    def _make_fake_nodes(self):
        return [
            {"id": '1', "cpu": {'count': 2},
             "ram": 1024, "storage": 256,
             "nw": 'nw1', "location": 'location1',
             "uuid": 'fe542581-97fe-4dbb-a1da-2daf0cf439ea'
             },
            {"id": '2', "cpu": {'count': 4},
             "ram": 2048, "storage": 500,
             "nw": 'nw2', "location": 'location2',
             "uuid": 'f0f96c58-d3d0-4292-a191-107e62e340c9'
             }
        ]
