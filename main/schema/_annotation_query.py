annotation_filter_parameter_schema = [
    {
        'name': 'media_id',
        'in': 'query',
        'required': False,
        'description': 'Comma-separated list of media IDs.',
        'explode': False,
        'schema': {
            'type': 'array',
            'items': {'type': 'integer'},
        },
    },
    {
        'name': 'type',
        'in': 'query',
        'required': False,
        'description': 'Unique integer identifying a annotation type.',
        'schema': {'type': 'integer'},
    },
    {
        'name': 'version',
        'in': 'query',
        'required': False,
        'explode': False,
        'description': 'List of integers representing versions to fetch',
        'schema': {
            'type': 'array',
            'items': {'type': 'integer'},
        },
    },
    {
        'name': 'after',
        'in': 'query',
        'required': False,
        'description': 'If given, all results returned will be after the '
                       'localization with this ID. The `start` and `stop` '
                       'parameters are relative to this modified range.',
        'schema': {'type': 'integer'},
    },
]
