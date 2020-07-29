from flask import jsonify
from .utils import get_schema_from_hdmf_class
from pynwb import NWBHDF5IO


def index():

    # Read one nwb file and get schema from hdmf class
    io = NWBHDF5IO('/home/vinicius/Área de Trabalho/Trabalhos/neuro_react/data/102086.nwb', mode='r')
    nwb = io.read()
    schema = get_schema_from_hdmf_class(nwb.subject)

    schema2 = get_schema_from_hdmf_class(nwb.acquisition)

    return jsonify({'data': [schema, schema2]})