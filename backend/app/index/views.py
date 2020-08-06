from flask import jsonify, request
from .utils import yaml_to_json
from pynwb import NWBHDF5IO
import datetime
import yaml
import json


def get_index(forms, title):
    for i, e in enumerate(forms):
        if title in e.keys():
            return i
    return -1


def index():

    # Read one nwb file and get schema from hdmf class
    yaml_path = '/home/vinicius/Área de Trabalho/Trabalhos/neuro/data/metadata.yaml'

    with open(yaml_path) as f:
        metadata = yaml.safe_load(f)

    schema = yaml_to_json(metadata)

    if request.method == 'POST':
        title = request.json['formTitle']
        form_index = get_index(schema, title)

        form_schema = schema[form_index]
        schema_aux = form_schema[title]

        for k, v in request.json['formData'].items():
            schema_aux['properties'][k]['default'] = v

        schema_json = {
            title: schema_aux
        }

        with open('{}_form.json'.format(title), 'w+') as out:
            json.dump(schema_json, out, indent=4)

        return jsonify({'response': 'ok'}), 200

    return jsonify({'data':schema})
