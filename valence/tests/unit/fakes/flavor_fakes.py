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


def fake_flavor_nodes():
    return [
        {"id": '1', "cpu": {'count': 2},
         "ram": 1024, "storage": 256,
         "nw": 'nw1', "location": 'location:1',
         "uuid": 'fe542581-97fe-4dbb-a1da'
         },
        {"id": '2', "cpu": {'count': 4},
         "ram": 2048, "storage": 500,
         "nw": 'nw2', "location": 'location:2',
         "uuid": 'f0f96c58-d3d0-4292-a191'
         }
    ]


def fake_assettag_flavors():
    return [json.dumps([{"flavor":
                        {"name": "L_irsd-location:2",
                         "ram": 2048,
                         "vcpus": 4,
                         "disk": 500,
                         "id": "f0f96c58-d3d0-4292-a191"}},
                        {"extra_specs": {"location:": "2"}}]),
            json.dumps([{"flavor":
                        {"name": "M_irsd-location:2",
                         "ram": 1024,
                         "vcpus": 2,
                         "disk": 250,
                         "id": "f0f96c58-d3d0-4292-a191"}},
                        {"extra_specs": {"location:": "2"}}]),
            json.dumps([{"flavor":
                        {"name": "S_irsd-location:2",
                         "ram": 512,
                         "vcpus": 1,
                         "disk": 125,
                         "id": "f0f96c58-d3d0-4292-a191"}},
                        {"extra_specs": {"location:": "2"}}])]


def fake_default_flavors():
    return [json.dumps([{"flavor":
                        {"name": "L_irsd-2",
                         "ram": 2048,
                         "vcpus": 4,
                         "disk": 500,
                         "id": "f0f96c58-d3d0-4292-a191"}},
                        {"extra_specs": {"location": "2"}}]),
            json.dumps([{"flavor":
                        {"name": "M_irsd-2",
                         "ram": 1024,
                         "vcpus": 2,
                         "disk": 250,
                         "id": "f0f96c58-d3d0-4292-a191"}},
                        {"extra_specs": {"location": "2"}}]),
            json.dumps([{"flavor":
                        {"name": "S_irsd-2",
                         "ram": 512,
                         "vcpus": 1,
                         "disk": 125,
                         "id": "f0f96c58-d3d0-4292-a191"}},
                        {"extra_specs": {"location": "2"}}])]
