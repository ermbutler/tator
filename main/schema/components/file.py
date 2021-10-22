from types import SimpleNamespace

file_fields = SimpleNamespace(
    created_datetime="created_datetime",
    created_by="created_by",
    modified_datetime="modified_datetime",
    modified_by="modified_by",
    description="description",
    path="path",
    id="id",
    name="name",
    project="project",
    attributes="attributes")

file_post_properties = {
    file_fields.name: {
        "type": "string",
        "description": "Name of file"
    },
    file_fields.path: {
        "type": "string",
        "description": "Server path to file"
    },
    file_fields.description: {
        "type": "string",
        "description": "Description of file"
    },
    file_fields.attributes: {
        'description': 'Object containing attribute values',
        'type': 'object',
        'additionalProperties': {'$ref': '#/components/schemas/AttributeValue'},
    },
}

# Note: While project is required, it's part of the path parameter(s)
file_spec = {
    'type': 'object',
    'description': 'Register non-media file spec',
    'properties': {
        **file_post_properties,
    },
}

file = {
    "type": "object",
    "description": "Non-media file spec.",
    "properties": {
        file_fields.id: {
            "type": "integer",
            "description": "Unique integer identifying the non-media file",
        },
        file_fields.project: {
            "type": "integer",
            "description": "Unique integer identifying the project associated with the file",
        },
        file_fields.created_datetime: {
            'type': 'string',
            'format': 'date-time',
            'description': 'Datetime this file was created',
        },
        file_fields.created_by: {
            'type': 'integer',
            'description': 'User that created this file'
        },
        file_fields.modified_datetime: {
            'type': 'string',
            'format': 'date-time',
            'description': 'Datetime this file was created',
        },
        file_fields.modified_by: {
            'type': 'integer',
            'description': 'User who last edited this file'
        },
        **file_post_properties
    },
}