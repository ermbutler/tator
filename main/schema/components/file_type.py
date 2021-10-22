file_type_properties = {
    'name': {
        'description': 'Name of the file type.',
        'type': 'string',
    },
    'description': {
        'description': 'Description of the file type.',
        'type': 'string',
        'default': '',
    },
    'attribute_types': {
        'description': 'Attribute type definitions.',
        'type': 'array',
        'items': {'$ref': '#/components/schemas/AttributeType'},
    },
}

file_type_spec = {
    'type': 'object',
    'required': ['name'],
    'properties': file_type_properties,
}

file_type = {
    'type': 'object',
    'description': 'File type.',
    'properties': {
        'id': {
            'type': 'integer',
            'description': 'Unique integer identifying a file type.',
        },
        'project': {
            'type': 'integer',
            'description': 'Unique integer identifying project for this file type.',
        },
        **file_type_properties,
    },
}