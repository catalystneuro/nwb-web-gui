from copy import deepcopy


def get_schema(docval):
    schema_base = dict(
        required=[],
        properties={},
        type='object',
        additionalProperties=False)

    schema = deepcopy(schema_base)

    for docval_arg in docval['args']:
        if docval_arg['type'] is str or (isinstance(docval_arg['type'], tuple) and str in docval_arg['type']):
            schema['properties'][docval_arg['name']] = {'type':'string', 'description':docval_arg['doc']}
            if 'default' in docval_arg:
                if docval_arg['default'] is not None:
                    schema['properties'][docval_arg['name']]['default'] = docval_arg['default']
            else:
                schema['required'].append(docval_arg['name'])

    return schema


def get_schema_from_hdmf_class(hdmf_class):
    return get_schema(hdmf_class.__init__.__docval__)