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

from valence.db import models


def fake_flavor():
    return {
        "uuid": "00000000-0000-0000-0000-000000000000",
        "name": "Flavor 1",
        "properties": {
            "memory": {
                "capacity_mib": "1000",
                "type": "DDR2"
            },
            "processor": {
                "total_cores": "2",
                "model": "Intel"
            },
            "pci_device": {
                "type": ["SSD", "NIC"]
            }
        }
    }


def fake_flavor_model():
    return models.Flavor(**fake_flavor())


def fake_flavor_list():
    return [
        {
            "uuid": "00000000-0000-0000-0000-000000000000",
            "name": "Flavor 1",
            "properties": {
                "memory": {
                    "capacity_mib": "1000",
                    "type": "DDR2"
                },
                "processor": {
                    "total_cores": "10",
                    "model": "Intel"
                },
                "pci_device": {
                    "type": ["NIC"]
                }
            }
        },
        {
            "uuid": "11111111-1111-1111-1111-111111111111",
            "name": "Flavor 2",
            "properties": {
                "memory": {
                    "capacity_mib": "2000",
                    "type": "DDR3"
                },
                "processor": {
                    "total_cores": "20",
                    "model": "Intel"
                },
                "pci_device": {
                    "type": ["SSD"]
                }
            }
        },
        {
            "uuid": "22222222-2222-2222-2222-222222222222",
            "name": "Flavor 3",
            "properties": {
                "memory": {
                    "capacity_mib": "3000",
                    "type": "SDRAM"
                },
                "processor": {
                    "total_cores": "30",
                    "model": "Intel"
                },
                "pci_device": {
                    "type": ["SSD", "NIC"]
                }
            }
        }
    ]


def fake_flavor_model_list():
    values_list = fake_flavor_list()
    for i in range(len(values_list)):
        values_list[i] = models.Flavor(**values_list[i])

    return values_list
