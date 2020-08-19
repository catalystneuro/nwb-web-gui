import pynwb
import inspect
from copy import deepcopy
import numpy as np

base_schema = dict(
    required=[],
    properties={},
    type='object',
    additionalProperties=False
)


def get_schema_from_hdmf_class(hdmf_class):
    """Get JSON schema from HDMF class"""
    class_name = hdmf_class.__module__ + '.' + hdmf_class.neurodata_type
    docval = hdmf_class.__init__.__docval__

    schema = deepcopy(base_schema)
    schema['title'] = class_name
    for docval_arg in docval['args']:
        # If simple type, store in tuple for next steps comparisons
        if not isinstance(docval_arg['type'], tuple):
            item_types = (docval_arg['type'], )
        else:
            item_types = docval_arg['type']

        # If item is a float
        if 'float' in item_types:
            schema_arg = dict(type='number', description=docval_arg['doc'])
        # If item it is a string
        elif str in item_types:
            schema_arg = dict(type='string', description=docval_arg['doc'])
        # If item is link to Device
        elif pynwb.device.Device in item_types:
            schema_arg = dict(type='object', description=docval_arg['doc'])
            schema_arg['properties'] = {
                'target': {"type": "string"}
            }
        # If item is a pynwb object
        elif any([getattr(it, '__module__', None).split('.')[0] == pynwb.__name__ for it in item_types]):
            schema_arg = dict(type='object', description=docval_arg['doc'])
            index = np.where([getattr(it, '__module__', None).split('.')[0] == pynwb.__name__ for it in item_types])[0][0]
            child_schema = get_schema_from_hdmf_class(hdmf_class=item_types[index])
            schema_arg.update(properties=child_schema)
        # If list of items - TODO
        elif list in item_types:
            # schema_arg = dict(name=docval_arg['name'], type='array', description=docval_arg['doc'])
            # schema_arg["items"] = {"type": "number"}
            continue

        # If field has default value, otherwise it is required
        if 'default' in docval_arg:
            if docval_arg['default'] is not None:
                schema_arg.update(default=docval_arg['default'])
        else:
            schema['required'].append(docval_arg['name'])

        # Update field properties
        schema['properties'][docval_arg['name']] = schema_arg

    if 'allow_extra' in docval:
        schema['additionalProperties'] = docval['allow_extra']

    return schema
