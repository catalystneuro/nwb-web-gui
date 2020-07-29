from flask import jsonify


def index():

    # Example of json schema generated from nwb file
    json = {
        "data":{
            "additionalProperties": False,
            "properties": {
                "def_key_name": {
                "default": "name",
                "description": "the default key name",
                "type": "string"
                },
                "label": {
                "description": "the label on this dictionary",
                "type": "string"
                }
            },
            "required": [
                "label"
            ],
            "type": "object"
            }
        }


    return jsonify(json)