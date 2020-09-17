import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, ALL, MATCH
import dash_bootstrap_components as dbc
import sd_material_ui as sdm
import numpy as np
import json
import yaml
import base64
from .converter_utils.forms import SchemaFormContainer
from pathlib import Path
import flask


class ConverterForms(html.Div):
    def __init__(self, parent_app):
        super().__init__([])
        self.parent_app = parent_app

        examples_path = Path(__file__).parent.absolute() / 'example_schemas'
        self.downloads_path = Path(__file__).parent.parent.parent.parent.parent.absolute() / 'downloads'

        source_schema_path = examples_path / 'schema_source.json'
        with open(source_schema_path, 'r') as inp:
            self.source_json_schema = json.load(inp)

        metadata_schema_path = examples_path / 'schema_metadata_all.json'
        with open(metadata_schema_path, 'r') as inp:
            self.metadata_json_schema = json.load(inp)

        # Fill form
        metadata_data_path = examples_path / 'metadata_example_0.json'
        with open(metadata_data_path, 'r') as inp:
            self.metadata_json_data = json.load(inp)

        # Source data Form
        self.source_forms = SchemaFormContainer(
            id='sourcedata',
            schema=self.source_json_schema,
            parent_app=self.parent_app
        )

        self.metadata_forms = None


        # Fill form
        #metadata_data_path = examples_path / 'metadata_example_0.json'
        #with open(metadata_data_path, 'r') as inp:
            #self.metadata_json_data = json.load(inp)
        #self.metadata_forms.update_data(data=self.metadata_json_data)

        self.children = [
            dbc.Container([
                # sdm.Drawer(
                #     id='left-drawer',
                #     open=True,
                #     children=[
                #         html.H4(children='Source Data'),
                #         html.Ul(children=[
                #             html.Li(children=['Source Files']),
                #             html.Li(children=['Conversion Options'])
                #         ]),
                #         html.H4(children='Metadata'),
                #         html.Ul(children=[
                #             html.Li(children=['NWBFile']),
                #             html.Li(children=['Subject']),
                #             html.Li(children=['Ecephys']),
                #             html.Li(children=['Ophys']),
                #             html.Li(children=['Behavior'])
                #         ]),
                #         html.H4(children='Conversion')
                #     ]
                # ),
                dbc.Row([
                    html.Br(),
                    dbc.Col(self.source_forms, width={'size': 12}),
                    dbc.Col(
                        dbc.Button('Get Metadata Form', id='get_metadata_btn', color='dark'),
                        style={'justify-content': 'left', 'text-align': 'left', 'margin-top': '1%'},
                        width={'size': 4}
                    )
                ]),
                dbc.Row([
                    dbc.Col(
                        dcc.Upload(dbc.Button('Load Metadata', color='dark'), id='button_load_metadata'),
                        width={'size': 2},
                        style={'justify-content': 'left', 'text-align': 'left', 'margin-top': '1%'},
                    ),
                    dbc.Col(
                        html.Div([
                            dbc.Button('Export Metadata', id='button_export_metadata', color='dark'),
                            dbc.Popover(
                                [
                                    dbc.PopoverBody([
                                        html.Div([
                                            html.A(
                                                dbc.Button("Download as JSON", id='button_export_json', color="link"),
                                                href='/downloads/exported_metadata.json'
                                            ),
                                            html.A(
                                                dbc.Button("Download as YAML", id='button_export_yaml', color="link"),
                                                href='/downloads/exported_metadata.yaml'
                                            )
                                        ])
                                    ])
                                ],
                                id="popover_export_metadata",
                                target='button_export_metadata',
                                is_open=False,
                                placement='top',
                            )
                        ]),
                        width={'size': 2},
                        style={'justify-content': 'left', 'text-align': 'left', 'margin-top': '1%'},
                    ),
                    dbc.Col(
                        dbc.Button('Refresh', id='button_refresh', color='dark'),
                        width={'size': 2},
                        style={'justify-content': 'left', 'text-align': 'left', 'margin-top': '1%'},
                    )
                ]),
                dbc.Row([
                    dbc.Col(
                        dbc.Alert(
                            children=[],
                            id="alert_required",
                            dismissable=True,
                            is_open=False,
                            color='danger'
                        )
                    )
                ]),
                dbc.Row(
                    [dbc.Col(id='metadata-col', width={'size': 12})],
                    style={'margin-top': '1%'}
                ),
                html.Div(id='hidden', style={'display': 'none'}),
                dbc.Row(
                    dbc.Col(
                        dbc.InputGroup(
                            [
                                dbc.InputGroupAddon("Output file: ", addon_type="prepend"),
                                dbc.Input(id="output-nwbfile-name", placeholder="filename.nwb"),
                                dbc.InputGroupAddon(
                                    dbc.Button('Run Conversion', id='button_run_conversion'),
                                    addon_type="append",
                                ),
                            ]
                        ),
                        width={'size': 11}
                    ),
                    style={'text-align': 'left', 'margin-top': '1%'}
                ),
                dbc.Textarea(
                    id='text-conversion-results',
                    className='string_input',
                    bs_size="lg",
                    readOnly=True,
                    style={'font-size': '16px'}
                ),
                html.Br(),
            ], style={'min-height': '110vh'})
        ]

        @self.parent_app.callback(
            Output('metadata-col', 'children'),
            [Input('get_metadata_btn', 'n_clicks')]
        )
        def get_metadata(click):
            if click and self.metadata_forms is None:
                # Metadata Form
                self.metadata_forms = SchemaFormContainer(
                    id='metadata',
                    schema=self.metadata_json_schema,
                    parent_app=self.parent_app
                )
                self.metadata_forms.update_data(data=self.metadata_json_data)
                return self.metadata_forms
            else:
                return self.metadata_forms

        @self.parent_app.callback(
            Output({'type': 'external-trigger-update-forms-values', 'index': 'metadata-external-trigger-update-forms-values'}, 'children'),
            [Input('button_load_metadata', 'contents'), Input('button_refresh', 'n_clicks')],
            [State('button_load_metadata', 'filename')]
        )
        def update_forms_values_metadata(contents, refresh, filename):
            """
            Updates forms values (except links) when:
            - Forms are created (receives metadata dict from Converter)
            - User uploads metadata json / yaml file
            """
            ctx = dash.callback_context
            trigger_source = ctx.triggered[0]['prop_id'].split('.')[0]

            if trigger_source == 'button_load_metadata':
                content_type, content_string = contents.split(',')
                filename_extension = filename.split('.')[-1]

                # Update SchemaFormContainer internal data dictionary
                if filename_extension == 'json':
                    bs4decode = base64.b64decode(content_string)
                    json_string = bs4decode.decode('utf8').replace("'", '"')
                    self.metadata_json_data = json.loads(json_string)
                    self.metadata_forms.update_data(data=self.metadata_json_data)
                elif filename_extension in ['yaml', 'yml']:
                    bs4decode = base64.b64decode(content_string)
                    yaml_data = yaml.load(bs4decode, Loader=yaml.BaseLoader)
                    self.metadata_json_data = yaml_data
                    self.metadata_forms.update_data(data=self.metadata_json_data)
                # Trigger update of React components
                output = str(np.random.rand())

                return output
            elif trigger_source == 'button_refresh':
                output = 'refresh_trigger'
                return output
            else:
                output = []
                return output

        @self.parent_app.callback(
            [
                Output("popover_export_metadata", "is_open"),
                Output('alert_required', 'is_open'),
                Output('alert_required', 'children'),
            ],
            [Input('button_export_metadata', 'n_clicks')],
            [
                State("popover_export_metadata", "is_open"), 
                State('alert_required', 'is_open'),
                State({'type': 'metadata-input', 'data_type': 'boolean','index': ALL}, 'checked'),
                State({'type': 'metadata-input', 'data_type': 'string','index': ALL}, 'value'),
                State({'type': 'metadata-input', 'data_type': 'datetime','index': ALL}, 'value'),
                State({'type': 'metadata-input', 'data_type': 'tags','index': ALL}, 'value'),
                State({'type': 'metadata-input', 'data_type': 'link','index': ALL}, 'value'),
                State({'type': 'metadata-input', 'data_type': 'name','index': ALL}, 'value'),
                State({'type': 'metadata-input', 'data_type': 'number','index': ALL}, 'value'),
                State({'type': 'metadata-input', 'data_type': ALL,'index': ALL}, 'id'),
            ] 
        )
        def export_metadata(click, fileoption_is_open, req_is_open, boolean_values, string_values, datetime_values, tags_values, link_values, name_values, number_values, ids):
            ctx = dash.callback_context
            trigger_source = ctx.triggered[0]['prop_id'].split('.')[0]

            # Prevent default
            if not click:
                return fileoption_is_open, req_is_open, []

            # If popover was opened, just close it
            if fileoption_is_open:
                return not fileoption_is_open, req_is_open, []

            # If no metadata form defined
            if self.metadata_forms is None:
                alert = [html.A('No metadata forms defined', href="#" + 'metadata-forms-error', className="alert-link")]
                return fileoption_is_open, not req_is_open, alert

            # Controllers and Variables
            alert_children = [
                html.H4("There are missing required fields:", className="alert-heading"),
                html.Hr()
            ]
            datetime_counter = 0
            string_counter = 0
            tags_counter = 0
            link_counter = 0
            names_counter = 0
            number_counter = 0
            empty_required_fields = []

            dicts_list = []
            output = dict()

            # Read data current from each field
            for e in ids:
                for k, v in self.metadata_forms.data.items():
                    if e['index'] == k:
                        if e['data_type'] == 'datetime':
                            field_value = datetime_values[datetime_counter]
                            datetime_counter += 1
                        elif e['data_type'] == 'string':
                            field_value = string_values[string_counter]
                            string_counter += 1
                        elif e['data_type'] == 'name':
                            field_value = name_values[names_counter]
                            names_counter += 1
                        elif e['data_type'] == 'number':
                            field_value = number_values[number_counter]
                            number_counter += 1
                        elif e['data_type'] == 'tags':
                            field_value = tags_values[tags_counter]
                            tags_counter += 1
                        elif e['data_type'] == 'link':
                            field_value = link_values[link_counter]
                            link_counter += 1

                        if v['required']:
                            if field_value is None or (isinstance(field_value, str) and field_value.isspace()) or field_value == '':
                                empty_required_fields.append(k)
                                alert_children.append(html.A(
                                    k,
                                    href="#" + 'wrapper-' + v['compound_id']['index'] + '-' + v['compound_id']['type'],
                                    className="alert-link"
                                ))
                                alert_children.append(html.Hr())
                        if field_value not in ['', None]:
                            v['value'] = field_value
                            splited_keys = k.split('-')
                            master_key_name = splited_keys[0]
                            field_name = splited_keys[-1]

                            for element in reversed(splited_keys):
                                if element == field_name:
                                    curr_dict = {field_name: v['value']}
                                else:
                                    curr_dict = {element: curr_dict}
                                if element == master_key_name:
                                    dicts_list.append(curr_dict)

            # Create nested output dict
            for e in dicts_list:
                master_key_name = list(e.keys())[0]
                output = ConverterForms._create_nested_dict(data=e, output=output, master_key_name=master_key_name)

            # If required fields missing return alert
            if len(empty_required_fields) > 0:
                return fileoption_is_open, not req_is_open, alert_children

            # Make temporary files on server side
            # JSON
            exported_file_path = self.downloads_path / 'exported_metadata.json'
            with open(exported_file_path, 'w') as outfile:
                json.dump(output, outfile, indent=4)

            # YAML
            exported_file_path = self.downloads_path / 'exported_metadata.yaml'
            with open(exported_file_path, 'w') as outfile:
                yaml.dump(output, outfile, default_flow_style=False)

            return not fileoption_is_open, req_is_open, []

        @self.parent_app.server.route('/downloads/<path:filename>')
        def download_file(filename):

            return flask.send_from_directory(
                directory=self.downloads_path,
                filename=filename,
                as_attachment=True
            )

        @self.parent_app.callback(
            Output("text-conversion-results", "value"),
            [Input('button_run_conversion', 'n_clicks')]
        )
        def run_conversion(click):
            """Run conversion """
            if click:
                return "This will call NWBConverter.run_conversion() and print results."
            return ""

    @staticmethod
    def _create_nested_dict(data, output, master_key_name):
        for k, v in data.items():
            if isinstance(v, dict):
                if k == master_key_name and k not in output:
                    output[k] = {}
                    ConverterForms._create_nested_dict(v, output[k], master_key_name)
                elif k != master_key_name and k not in output:
                    output[k] = {}
                    ConverterForms._create_nested_dict(v, output[k], master_key_name)
                else:
                    ConverterForms._create_nested_dict(v, output[k], master_key_name)
            else:
                if isinstance(v, list):
                    element = [e['displayValue'] for e in v]
                else:
                    element = v
                output[k] = element

        return output
