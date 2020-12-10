from nwb_conversion_tools import NWBConverter
from pathlib import Path
import json


class ExampleNWBConverter(NWBConverter):
    data_interface_classes = {}

    def __init__(self, **input_args):
        super().__init__(**input_args)

    @classmethod
    def get_conversion_options_schema(cls):
        examples_path = Path(__file__).parent.parent.absolute() / 'example_schemas'
        conversion_options_schema = examples_path / 'schema_conversion_example.json'
        with open(conversion_options_schema, 'r') as inp:
            conversion_schema = json.load(inp)

        return conversion_schema

    @classmethod
    def get_source_schema(cls):
        examples_path = Path(__file__).parent.parent.absolute() / 'example_schemas'
        source_schema_path = examples_path / 'schema_source.json'
        with open(source_schema_path, 'r') as inp:
            source_schema = json.load(inp)

        return source_schema

    def get_metadata_schema(self):
        examples_path = Path(__file__).parent.parent.absolute() / 'example_schemas'
        metadata_schema_path = examples_path / 'schema_metadata.json'
        with open(metadata_schema_path, 'r') as inp:
            metadata_schema = json.load(inp)
        return metadata_schema

    def get_metadata(self):
        examples_path = Path(__file__).parent.parent.absolute() / 'example_schemas'
        metadata_data_path = examples_path / 'metadata_example.json'
        with open(metadata_data_path, 'r') as inp:
            metadata = json.load(inp)
        return metadata

    def run_conversion(self, metadata, nwbfile_path, save_to_file, conversion_options):
        raise NotImplementedError('TODO')
