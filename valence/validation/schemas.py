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

import jsonschema

flavor_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'description': {'type': 'string'},
        'properties': {
            'type': 'object',
            'properties': {
                'memory': {
                    'type': 'object',
                    'properties': {
                        'capacity_mib': {'type': 'string'},
                        'type': {'type': 'string'}
                    },
                    'additionalProperties': False,
                },
                'processor': {
                    'type': 'object',
                    'properties': {
                        'total_cores': {'type': 'string'},
                        'model': {'type': 'string'},
                    },
                    'additionalProperties': False,
                },
                'pci_device': {
                    'type': 'object',
                    'properties': {
                        'type': {'type': 'array'}
                    },
                    'additionalProperties': False,
                },
            },
            'additionalProperties': False,
        },
    },
    'required': ['name', 'properties'],
    'additionalProperties': False,
}

jsonschema.Draft4Validator.check_schema(flavor_schema)

podmanager_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'url': {
            'type': 'string',
            'format': 'uri',
            },
        'driver': {'type': 'string'},
        'authentication': {
            'type': 'array',
            'minItems': 1,
            'items': {
                'type': 'object',
                'properties': {
                    'type': {'type': 'string'},
                    'auth_items': {
                        'type': 'object',
                        'properties': {
                            'username': {'type': 'string'},
                            'password': {'type': 'string'},
                        },
                        'required': ['username', 'password'],
                        'additionalProperties': False,
                    },
                },
                'required': ['type', 'auth_items'],
                'additionalProperties': False,
            },
        },
    },
    'required': ['name', 'url', 'authentication'],
    'additionalProperties': False,
}

jsonschema.Draft4Validator.check_schema(podmanager_schema)

compose_node_with_flavor = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'description': {'type': 'string'},
        'flavor_id': {'type': 'string'},
        'podm_id': {'type': 'string'}
    },
    'required': ['name', 'flavor_id'],
    'additionalProperties': False,
}

compose_node_with_properties = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'description': {'type': 'string'},
        'podm_id': {'type': 'string'},
        'properties': {
            'type': 'object',
            'properties': {
                'memory': {
                    'type': 'object',
                    'properties': {
                        'capacity_mib': {'type': 'string'},
                        'type': {'type': 'string'}
                    },
                    'additionalProperties': False,
                },
                'processor': {
                    'type': 'object',
                    'properties': {
                        'total_cores': {'type': 'string'},
                        'model': {'type': 'string'},
                    },
                    'additionalProperties': False,
                },
                'pci_device': {
                    'type': 'object',
                    'properties': {
                        'type': {'type': 'array'}
                    },
                    'additionalProperties': False,
                },
            },
            'additionalProperties': False,
        },
    },
    'required': ['name'],
    'additionalProperties': False,
}

compose_node_schema = {
    'anyOf': [
        compose_node_with_flavor,
        compose_node_with_properties
        ]
}

jsonschema.Draft4Validator.check_schema(compose_node_schema)

node_manage_schema = {
    'type': 'object',
    'properties': {
        'node_index': {'type': 'string'},
        'podm_id': {'type': 'string'},
    },
    'required': ['node_index'],
    'additionalProperties': False,
}

jsonschema.Draft4Validator.check_schema(node_manage_schema)

node_action_schema = {
    'type': 'object',
    'properties': {
        'Boot': {
            'type': 'object',
            'properties': {
                'Enabled': {
                    'enum': ['Once', 'Continuous']
                    },
                'Target': {
                    'enum': ['Pxe', 'Hdd', 'None']
                    },
            },
            'required': ['Enabled', 'Target'],
            'additionalProperties': False,
        },
        'Reset': {
            'type': 'object',
            'properties': {
                'Type': {
                    'enum': ['On', 'ForceOn', 'ForceOff', 'GracefulRestart']
                    },
            },
            'required': ['Type'],
            'additionalProperties': False,
        },
        'attach': {
            'type': 'object',
            'properties': {
                'resource_id': {'type': 'string'},
            },
            'required': ['resource_id'],
            'additionalProperties': False,
        },
        'detach': {
            'type': 'object',
            'properties': {
                'resource_id': {'type': 'string'},
            },
            'required': ['resource_id'],
            'additionalProperties': False,
        },
    },
    'oneOf': [
        {'required': ['Boot']},
        {'required': ['Reset']},
        {'required': ['attach']},
        {'required': ['detach']},
    ],
    'additionalProperties': False,
}

jsonschema.Draft4Validator.check_schema(node_action_schema)

SCHEMAS = {'flavor_schema': flavor_schema,
           'podmanager_schema': podmanager_schema,
           'compose_node_schema': compose_node_schema,
           'node_manage_schema': node_manage_schema,
           'node_action_schema': node_action_schema, }
