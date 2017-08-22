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


def get_test_composed_node(**kwargs):
    return {
        'uuid': kwargs.get('uuid', 'ea8e2a25-2901-438d-8157-de7ffd68d051'),
        'name': kwargs.get('name', 'fake_name'),
        'podm_id': kwargs.get('podm_id', '78e2a25-2901-438d-8157-de7ffd68d05'),
        'description': kwargs.get('description', 'fake_description'),
        'boot_source': kwargs.get('boot_source', 'Hdd'),
        'health_status': kwargs.get('health_status', 'OK'),
        'index': kwargs.get('index', '1'),
        'node_power_state': kwargs.get('node_power_state', 'On'),
        'node_state': kwargs.get('node_state', 'Assembling'),
        'pooled_group_id': kwargs.get('bookmark_link', 'None'),
        'target_boot_source': kwargs.get('target_boot_source', 'Hdd'),
        'resource_uri': kwargs.get(
            'resource_uri',
            'nodes/7be5bc10-dcdf-11e6-bd86-934bc6947c55/'),
        'metadata': kwargs.get(
            'metadata',
            {'memory': [{'data_width_bit': 0,
                         'speed_mhz': 2400,
                         'total_memory_mb': 8192}],
             'network': [{'ipv4': [{'address': '192.168.0.10',
                                    'gateway': '192.168.0.1',
                                    'subnet_mask': '255.255.252.0'}],
                          'mac': 'e9:47:d3:60:64:66',
                          'speed_mbps': 0,
                          'status': 'Enabled',
                          'vlans': [{'status': 'Enabled',
                                     'vlanid': 99}]}],
             'processor': [{'instruction_set': None,
                            'model': 'None',
                            'speed_mhz': 3700,
                            'total_core': 2}]})
    }


def get_test_node_list(**kwargs):
    return [
        {
            'uuid': kwargs.get('uuid', '11111111-1111-1111-1111-111111111111'),
            'name': kwargs.get('name', 'node_1'),
            'index': kwargs.get('index', '1')
        },
        {
            'uuid': kwargs.get('uuid', '22222222-2222-2222-2222-222222222222'),
            'name': kwargs.get('name', 'node_2'),
            'index': kwargs.get('index', '2')
        },
        {
            'uuid': kwargs.get('uuid', '33333333-3333-3333-3333-333333333333'),
            'name': kwargs.get('name', 'node_3'),
            'index': kwargs.get('index', '3')
        }
    ]
