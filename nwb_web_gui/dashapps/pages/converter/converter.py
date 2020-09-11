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
from nwb_web_gui.dashapps.utils.make_components import make_modal
from pathlib import Path
import flask


class ConverterForms(html.Div):
    def __init__(self, parent_app):
        super().__init__([])
        self.parent_app = parent_app
        self.current_modal_source = ''
        modal = make_modal(parent_app)

        examples_path = Path(__file__).parent.absolute() / 'example_schemas'
        self.downloads_path = Path(__file__).parent.parent.parent.parent.parent.absolute() / 'downloads'

        source_schema_path = examples_path / 'schema_source.json'
        with open(source_schema_path, 'r') as inp:
            self.source_json_schema = json.load(inp)

        metadata_schema_path = examples_path / 'schema_metadata_all.json'
        with open(metadata_schema_path, 'r') as inp:
            self.metadata_json_schema = json.load(inp)

        # Source data Form
        self.source_forms = SchemaFormContainer(
            id='sourcedata',
            schema=self.source_json_schema,
            parent_app=self.parent_app
        )

        # Metadata Form
        self.metadata_forms = SchemaFormContainer(
            id='metadata',
            schema=self.metadata_json_schema,
            parent_app=self.parent_app
        )

        # Fill form
        metadata_data_path = examples_path / 'metadata_example_0.json'
        with open(metadata_data_path, 'r') as inp:
            self.metadata_json_data = json.load(inp)
        self.metadata_forms.update_data(data=self.metadata_json_data)

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
                        dbc.Button('Get Metadata Form', id='get_metadata_btn'),
                        style={'justify-content': 'left', 'text-align': 'left', 'margin-top': '1%'},
                        width={'size': 4}
                    )
                ]),
                dbc.Row([
                    dbc.Col(
                        dcc.Upload(dbc.Button('Load Metadata'), id='button_load_metadata'),
                        width={'size': 2},
                        style={'justify-content': 'left', 'text-align': 'left', 'margin-top': '1%'},
                    ),
                    dbc.Col(
                        html.Div([
                            dbc.Button('Export Metadata', id='button_export_metadata'),
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
                        dbc.Button('Refresh', id='button_refresh'),
                        width={'size': 2},
                        style={'justify-content': 'left', 'text-align': 'left', 'margin-top': '1%'},
                    )
                ]),
                dbc.Row([
                    dbc.Col(
                        dbc.Alert(
                            "Required fields missing",
                            id="alert_required",
                            dismissable=True,
                            is_open=False,
                            color='danger'
                        )
                    )
                ]),
                dbc.Row(
                    [dbc.Col(self.metadata_forms, width={'size': 12})],
                    style={'margin-top': '1%'}
                ),
                dbc.Row(modal),
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
                html.Br()
            ], style={'min-height': '110vh'})
        ]

        @self.parent_app.callback(
            Output('modal_explorer', 'is_open'),
            [Input({'type': 'source_explorer', 'index': ALL}, 'n_clicks'), Input('close_explorer_modal', 'n_clicks')],
            [State("modal_explorer", "is_open")]
        )
        def open_explorer(click_open, click_close, is_open):

            ctx = dash.callback_context
            source = ctx.triggered[0]['prop_id'].split('.')[0]

            if 'index' in source:
                dict_source = json.loads(source)

                self.current_modal_source = dict_source['index']

            if source != '' and (any(click_open) or click_close):
                return not is_open
            else:
                return is_open

        @self.parent_app.callback(
            Output({'type': 'source_string_input', 'index': MATCH}, 'value'),
            [Input('submit_file_browser_modal', 'n_clicks')],
            [
                State('chosen_file_modal', 'value'),
                State({'type': 'source_string_input', 'index': MATCH}, 'value'),
                State({'type': 'source_string_input', 'index': MATCH}, 'id'),
            ]
        )
        def change_path_values(click, input_value, values, ids):
            ctx = dash.callback_context
            source = ctx.triggered[0]['prop_id'].split('.')[0]

            if self.current_modal_source.replace('explorer', 'input') == ids['index'] and input_value != '':
                return input_value
            else:
                return values

        @self.parent_app.callback(
            Output('metadata-trigger-update-forms-values', 'children'),
            [Input('button_load_metadata', 'contents')],
            [State('button_load_metadata', 'filename')]
        )
        def update_forms_values_metadata(contents, filename):
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
            else:
                output = []
                return output

        @self.parent_app.callback(
            [Output("popover_export_metadata", "is_open"), Output('alert_required', 'is_open')],
            [Input('button_export_metadata', 'n_clicks')],
            [State("popover_export_metadata", "is_open"), State('alert_required', 'is_open')] +
            [State(v['compound_id'], 'value') for v in self.metadata_forms.data.values()]
        )
        def export_metadata(click, fileoption_is_open, req_is_open, *form_values):
            """
            Exports data to JSON or YAML files.
            """

            ctx = dash.callback_context
            trigger_source = ctx.triggered[0]['prop_id'].split('.')[0]

            output = dict()
            dicts_list = []
            empty_required_fields = []
            if click:
                # If popover was opened, just close it
                if fileoption_is_open:
                    return not fileoption_is_open, req_is_open
                # If popover was closed, make files and open options
                else:
                    for i, (k, v) in enumerate(self.metadata_forms.data.items()):
                        # Read data current from each field
                        field_value = form_values[i]
                        if v['required']:
                            if form_values[i] is None:
                                empty_required_fields.append(k)
                            elif isinstance(form_values[i], str):
                                if form_values[i].isspace() or form_values[i] == '':
                                    empty_required_fields.append(k)
                            elif form_values[i] == '':
                                empty_required_fields.append(k)
                        # Ignore empty fields
                        if field_value not in ['', None]:
                            v['value'] = field_value
                            # Organize item inside the output dictionary
                            splited_keys = k.split('-')
                            master_key_name = splited_keys[0]
                            field_name = splited_keys[-1]

                            for e in reversed(splited_keys):
                                if e == field_name:
                                    curr_dict = {field_name: v['value']}
                                else:
                                    curr_dict = {e: curr_dict}
                                if e == master_key_name:
                                    dicts_list.append(curr_dict)

                    for e in dicts_list:
                        master_key_name = list(e.keys())[0]
                        output = ConverterForms._create_nested_dict(data=e, output=output, master_key_name=master_key_name)

                    # If required fields missing return alert
                    if len(empty_required_fields) > 0:
                        return fileoption_is_open, not req_is_open

                    # Make temporary files on server side
                    # JSON
                    exported_file_path = self.downloads_path / 'exported_metadata.json'
                    with open(exported_file_path, 'w') as outfile:
                        json.dump(output, outfile, indent=4)

                    # YAML
                    exported_file_path = self.downloads_path / 'exported_metadata.yaml'
                    with open(exported_file_path, 'w') as outfile:
                        yaml.dump(output, outfile, default_flow_style=False)

                    return not fileoption_is_open, req_is_open
            return fileoption_is_open, req_is_open

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
                output[k] = v

        return output
