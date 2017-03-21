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
SCHEMAS = {'flavor_schema': flavor_schema,
           'podmanager_schema': podmanager_schema, }
