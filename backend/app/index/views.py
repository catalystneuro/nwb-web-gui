from flask import jsonify, request
from pynwb import NWBHDF5IO
import datetime
import yaml
import json
from werkzeug.utils import secure_filename
from flask import current_app as app
from pathlib import Path
from .utils import yaml_to_json, get_index, ovewrite_schemas

schema = [1]
inputSchema = [1]
nwb_save_path = None
new_schema = []


def upload_file():
    global schema
    global new_schema
    global inputSchema

    if 'input' in request.files.keys():
        myFile = request.files['input'] 
        filename = secure_filename(myFile.filename)
        destination = Path(app.root_path) / "uploads/metadata/inputsMetadata.json"
        myFile.save(str(destination))
        with open(destination, 'r') as inp:
            inputSchema = json.load(inp)

        return jsonify({'schemaOne': inputSchema}), 200
    else:
        myFile = request.files['nwb'] 
        filename = secure_filename(myFile.filename)
        destination = Path(app.root_path) / "uploads/metadata/metadata.json"
        myFile.save(str(destination))

        with open(destination, 'r') as inp:
            schema = json.load(inp)

        new_schema = schema

        return jsonify({'schemaTwo': schema}), 200


def save_all_schemas():
    global new_schema
    destination = Path(app.root_path) / "uploads/metadata/all_uploaded_metadata.json"
    with open(destination, 'w+') as out:
        json.dump(new_schema, out, indent=4)

    return jsonify({'data':'ok'})


def save_metadata():
    global schema
    global inputSchema
    global new_schema

    if request.json is None:
        return jsonify({'error': 'error'}), 400

    title = request.json['formTitle']

    if 'input' not in title.lower() and 'clear' not in title.lower():
        form_index = get_index(schema, title)
        form_schema = schema[form_index]
        schema_aux = form_schema[title]
        schema_aux = ovewrite_schemas(schema_aux)
        new_schema_index = get_index(new_schema, title)
        schema_json = {
            title: schema_aux
        }
        if new_schema_index == -1:
            new_schema.append(schema_json)
        else:
            new_schema[new_schema_index] = schema_json
        save_all_schemas()
    elif 'clear' in title.lower():
        if request.json['formChoice'] == 'nwb':
            schema = [1]
            return jsonify({'schemaTwo': schema}), 200
        else:
            inputSchema = [1]
            return jsonify({'schemaOne': inputSchema}), 200
    else:
        form_index = get_index(inputSchema, title)
        form_schema = inputSchema[form_index]
        schema_aux = form_schema[title]
        schema_aux = ovewrite_schemas(schema_aux)
        schema_json = {
            title: schema_aux
        }

    dest = Path(app.root_path) / 'uploads/formData/{}_form.json'.format(title)

    with open(dest, 'w+') as out:
        json.dump(schema_json, out, indent=4)

    return jsonify({'response': 'ok'}), 200


def index():
    global schema
    global inputSchema
    global new_schema

    return jsonify({'schemaOne': inputSchema, 'schemaTwo': schema})


def convert_nwb():
    global nwb_save_path
    # Check if path exists
    #TODO
    path = Path(request.json['nwbPath'])
    if path.is_dir():
        nwb_save_path = path
        return jsonify({'data': 'ok'}), 200
    else:
        return jsonify({'data':'error'}), 400