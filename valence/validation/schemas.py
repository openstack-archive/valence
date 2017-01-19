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
                        'memory_type': {'type': 'string'}
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
SCHEMAS = {'flavor_schema': flavor_schema}
