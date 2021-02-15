from types import SimpleNamespace

fields = SimpleNamespace(
    id='id',
    username='username',
    first_name='first_name',
    last_name='last_name',
    email='email')

user_properties = {
    fields.username: {
        'type': 'string',
        'description': 'Username of user.',
    },
    fields.first_name: {
        'type': 'string',
        'description': 'First name of user.',
    },
    fields.last_name: {
        'type': 'string',
        'description': 'Last name of user.',
    },
    fields.email: {
        'type': 'string',
        'description': 'Email address of user.',
    },
}

user_update = {
    'type': 'object',
    'properties': {
        fields.first_name: user_properties[fields.first_name],
        fields.last_name: user_properties[fields.last_name],
        fields.email: user_properties[fields.email],
    },
}

user = {
    'type': 'object',
    'properties': {
        fields.id: {
            'type': 'integer',
            'description': 'Unique integer identifying a user.',
        },
        **user_properties,
    },
}
