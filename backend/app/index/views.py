from flask import jsonify, request
from .utils import yaml_to_json
from pynwb import NWBHDF5IO
import datetime
import yaml
import json
from werkzeug.utils import secure_filename
from flask import current_app as app
from pathlib import Path

schema = [1]


def get_index(forms, title):
    for i, e in enumerate(forms):
        if title in e.keys():
            return i
    return -1


def index():
    global schema

    # Read one json file to create form schema
    nwb_json_path = '/home/vinicius/Área de Trabalho/Trabalhos/nwb-web-gui/metadataSchema.json'
    input_json_path = '/home/vinicius/Área de Trabalho/Trabalhos/nwb-web-gui/inputsSchema.json'

    with open(input_json_path, 'r') as inp:
        schemaOne = json.load(inp)

    with open(nwb_json_path, 'r') as inp:
        schemaTwo = json.load(inp)


    # If sending filled form data
    if request.method == 'POST' and not request.files:
        if request.json is None:
            return jsonify({'error': 'error'}), 400

        title = request.json['formTitle']

        print(title)

        if 'input' not in title.lower() and 'clear' not in title.lower():
            form_index = get_index(schema, title)
            form_schema = schema[form_index]
        elif 'clear' in title.lower():
            schema = [1]
            return jsonify({'schemaTwo': schema}), 200
        else:
            form_index = get_index(schemaOne, title)
            form_schema = schemaOne[form_index]

        schema_aux = form_schema[title]

        for k, v in request.json['formData'].items():
            schema_aux['properties'][k]['default'] = v

        schema_json = {
            title: schema_aux
        }
        dest = Path(app.root_path) / 'uploads/formData/{}_form.json'.format(title)

        with open(dest, 'w+') as out:
            json.dump(schema_json, out, indent=4)

            return jsonify({'response': 'ok'}), 200
    elif request.files:
        # if sending metatada json file (load metadata)
        myFile = request.files['myFile'] 
        filename = secure_filename(myFile.filename)

        destination = Path(app.root_path) / "uploads/metadata/metadata.json"
        myFile.save(destination)

        with open(destination, 'r') as inp:
            schema = json.load(inp)

        return jsonify({'schemaTwo': schema}), 200

    return jsonify({'schemaOne': schemaOne, 'schemaTwo':schema})
