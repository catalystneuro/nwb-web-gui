from copy import deepcopy
from flask import request


def ovewrite_schemas(schema_aux):
    for k, v in request.json['formData'].items():
        schema_aux['properties'][k]['default'] = v
    return schema_aux


def get_index(forms, title):
    for i, e in enumerate(forms):
        if title in e.keys():
            return i
    return -1


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


def yaml_to_json(yaml):
    forms_list = []

    for e in yaml:
        schema_base = dict(
            required=[],
            properties={},
            type='object',
            additionalProperties=False)

        for k,v in yaml[e].items():
            if k[0].islower():
                if k not in schema_base['required']:
                    schema_base['required'].append(k)
                schema_base['title'] = e
                if 'time' not in k:
                    schema_base['properties'][k] = {
                        'type': 'string',
                        'default':v,
                    }
                else:
                    schema_base['properties'][k] = {
                        'type': 'string',
                        'format': 'date-time',
                    }
            else:
                if isinstance(yaml[e][k], list):
                    for element in yaml[e][k]:
                        schema_base['title'] = e
                        for key, val in element.items():
                            if isinstance(element[key], list):
                                for item in element[key]:
                                    for i, value in item.items():
                                        form_name = '{} {} {} {}'.format(e, k, key, i)
                                        if form_name not in schema_base['required']:
                                            schema_base['required'].append(form_name)
                                        schema_base['properties'][form_name] = {
                                            'type':'string',
                                            'default': value
                                        }
                            else:
                                form_name = '{} {} {}'.format(e,k,key)
                                if form_name not in schema_base['required']:
                                    schema_base['required'].append(form_name)
                                schema_base['properties'][form_name] = {
                                    'type': 'string',
                                    'default': val
                                }

        forms_list.append({e:schema_base})

    return forms_list
