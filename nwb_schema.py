import inspect
from copy import deepcopy

base_schema = dict(
        required=[],
        properties=[],
        type='object',
        additionalProperties=False)


def get_schema_from_method_signature(class_method):

    input_schema = deepcopy(base_schema)

    for param in inspect.signature(class_method.__init__).parameters.values():
        if param.name is not 'self':
            arg_spec = dict(name=param.name, type='string')
            if param.default is param.empty:
                input_schema['required'].append(param.name)
            elif param.default is not None:
                arg_spec.update(default=param.default)
            input_schema['properties'].append(arg_spec)
        input_schema['additionalProperties'] = param.kind == inspect.Parameter.VAR_KEYWORD

    return input_schema


def get_schema_from_docval(docval):

    schema = deepcopy(base_schema)
    for docval_arg in docval['args']:
        # If simple type, store in tuple for next steps comparisons
        if not isinstance(docval_arg['type'], tuple):
            item_types = (docval_arg['type'], )
        else:
            item_types = docval_arg['type']

        # If item is a float
        if 'float' in item_types:
            schema_arg = dict(name=docval_arg['name'], type='number', description=docval_arg['doc'])
        # If item it is a string
        elif str in item_types:
            schema_arg = dict(name=docval_arg['name'], type='string', description=docval_arg['doc'])
        # TODO -
        elif list in item_types:
            print('skipped ', docval_arg['name'])
            continue
        # If item is a pynwb object - recurrently pass child to `get_schema_from_docval()`
        elif any([getattr(it, '__module__', None).split('.')[0] == pynwb.__name__ for it in item_types]):
            schema_arg = dict(name=docval_arg['name'], type='object', description=docval_arg['doc'])
            index = np.where([getattr(it, '__module__', None).split('.')[0] == pynwb.__name__ for it in item_types])[0][0]
            child_schema = get_schema_from_hdmf_class(hdmf_class=item_types[index])
            schema_arg.update(properties=child_schema)

        if 'default' in docval_arg:
            if docval_arg['default'] is not None:
                schema_arg.update(default=docval_arg['default'])
        else:
            schema['required'].append(docval_arg['name'])
        schema['properties'].append(schema_arg)

    if 'allow_extra' in docval:
        schema['additionalProperties'] = docval['allow_extra']

    return schema


def get_schema_from_hdmf_class(hdmf_class):
    return get_schema_from_docval(hdmf_class.__init__.__docval__)
