from flask import jsonify
from .utils import yaml_to_json
from pynwb import NWBHDF5IO
import datetime
import yaml


def index():

    # Read one nwb file and get schema from hdmf class
    yaml_path = '/home/vinicius/Área de Trabalho/Trabalhos/neuro/data/metadata.yaml'

    with open(yaml_path) as f:
        metadata = yaml.safe_load(f)

    schema = yaml_to_json(metadata)

    return jsonify({'data': schema})
