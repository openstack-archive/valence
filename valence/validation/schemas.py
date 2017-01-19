
node_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'description': {'type': 'string'},
    },
    'required': ['name'],
    'additionalProperties': False,
}

SCHEMAS = {'node_schema': node_schema}
