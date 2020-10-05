from nwb_conversion_tools import NWBConverter
from pathlib import Path
import json


class ExampleNWBConverter(NWBConverter):
    data_interface_classes = {}

    def __init__(self, **input_args):
        super().__init__(**input_args)

    @classmethod
    def get_input_schema(cls):
        examples_path = Path(__file__).parent.parent.absolute() / 'example_schemas'
        source_schema_path = examples_path / 'schema_source.json'
        with open(source_schema_path, 'r') as inp:
            input_schema = json.load(inp)
        return input_schema

    def get_metadata_schema(self, source_paths, conversion_options):
        examples_path = Path(__file__).parent.parent.absolute() / 'example_schemas'
        metadata_schema_path = examples_path / 'schema_metadata_all.json'
        with open(metadata_schema_path, 'r') as inp:
            metadata_schema = json.load(inp)
        return metadata_schema

    def get_metadata(self, source_paths, conversion_options):
        examples_path = Path(__file__).parent.parent.absolute() / 'example_schemas'
        metadata_data_path = examples_path / 'metadata_example_0.json'
        with open(metadata_data_path, 'r') as inp:
            metadata = json.load(inp)
        return metadata