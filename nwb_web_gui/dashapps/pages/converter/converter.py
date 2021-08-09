import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import numpy as np
import json
import yaml
import base64
from json_schema_to_dash_forms.forms import SchemaFormContainer
from pathlib import Path
import flask
from io import StringIO
from contextlib import redirect_stdout
import threading
import time
from nwb_conversion_tools.utils.json_schema import dict_deep_update


class ConverterForms(html.Div):
    def __init__(self, parent_app, converter_class):
        """
        Forms to interface user input with NWB converters.

        INPUT:
        ------
        parent_app : running Dash app
        converter : NWB converter class
        """
        super().__init__([])
        self.parent_app = parent_app
        self.converter_class = converter_class
        self.export_controller = False
        self.convert_controller = False
        self.get_metadata_controller = False
        self.conversion_messages = ''
        self.conversion_msg_controller = True
        self.msg_buffer = StringIO()

        self.downloads_path = Path(__file__).parent.parent.parent.parent.parent.absolute() / 'downloads'
        self.root_path = Path(self.parent_app.server.config['NWB_GUI_ROOT_PATH'])

        if not self.downloads_path.is_dir():
            self.downloads_path.mkdir()

        self.source_json_schema = converter_class.get_source_schema()
        self.conversion_json_schema = converter_class.get_conversion_options_schema()

        # Source data Form
        self.source_forms = SchemaFormContainer(
            id='sourcedata',
            schema=self.source_json_schema,
            parent_app=self.parent_app,
            root_path=self.root_path
        )

        # Conversion Option Form
        self.conversion_options_forms = SchemaFormContainer(
            id='conversiondata',
            schema=self.conversion_json_schema,
            parent_app=self.parent_app,
            root_path=self.root_path
        )

        self.metadata_forms = SchemaFormContainer(
            id='metadata',
            schema=dict(),
            parent_app=self.parent_app,
            root_path=self.root_path
        )
        self.style = {'background-color': '#f0f0f0', 'min-height': '100vh'}

        self.children = [
            html.Br(),
            dbc.Container([
                dbc.Row([
                    html.Br(),
                    dbc.Col(
                        dbc.Card([
                            dbc.Col(
                                html.H4('Source Data'),
                                style={'text-align': 'center', 'justify-content': 'center', "margin-top": "15px"},
                                width={'size': 12}
                            ),
                            dbc.CardBody(
                                self.source_forms
                            )
                        ], style={'background-color': '##eceef7', "box-shadow": "2px 2px 2px 2px rgba(0,0,0,0.1)"}),
                        width={'size': 12}
                    ),
                    dbc.Col(
                        dbc.Button('Get Metadata Form', id='get_metadata_btn', color='dark'),
                        style={'justify-content': 'left', 'text-align': 'left', 'margin-top': '1%'},
                        width={'size': 4}
                    )
                ]),
                dbc.Row([
                    dbc.Col(
                        dcc.Upload(dbc.Button('Load Metadata', color='dark'), id='button_load_metadata', style={'display': 'none'}),
                        width={'size': 2},
                        style={'justify-content': 'left', 'text-align': 'left', 'margin-top': '1%'},
                    ),
                    dbc.Col(
                        html.Div([
                            dbc.Button('Export Metadata', id='button_export_metadata', color='dark', style={'display': 'none'}),
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
                        dbc.Button('Refresh', id='button_refresh', color='dark', style={'display': 'none'}),
                        width={'size': 2},
                        style={'justify-content': 'left', 'text-align': 'left', 'margin-top': '1%'},
                    )
                ]),
                dbc.Row([
                    dbc.Col(
                        dbc.Alert(
                            children=[],
                            id="alert_required_source",
                            dismissable=True,
                            is_open=False,
                            color='danger'
                        )
                    ),
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
                    dbc.Col(id='metadata-col', width={'size': 12}),
                    style={'margin-top': '1%', 'margin-bottom': '10px'}
                ),
                dbc.Row(
                    dbc.Col([
                        dbc.Card([
                            dbc.Col(
                                html.H4('Conversion Options'),
                                style={'text-align': 'center', 'justify-content': 'center', "margin-top": "15px"},
                                width={'size': 12}
                            ),
                            dbc.CardBody(self.conversion_options_forms)
                        ], style={'background-color': '##eceef7', "box-shadow": "2px 2px 2px 2px rgba(0,0,0,0.1)"}),
                    ],
                        id='conversion-col',
                        width={'size': 12},
                        style={'display': 'none'}
                    )
                ),
                dbc.Row(
                    dbc.Col(
                        dbc.InputGroup(
                            [
                                dbc.InputGroupAddon("Output file: ", addon_type="prepend"),
                                dbc.Input(id="output-nwbfile-name", value=str(self.root_path)+'/'),
                                dbc.InputGroupAddon(
                                    dbc.Button('Run Conversion', id='button_run_conversion'),
                                    addon_type="append",
                                ),
                            ]
                        ),
                        width={'size': 11}
                    ),
                    style={'text-align': 'left', 'margin-top': '15px', 'display': 'none'},
                    id='row_output_conversion'
                ),
                dbc.Row([
                    dbc.Col(
                        dbc.Alert(
                            children=[],
                            id="alert-required-conversion",
                            dismissable=True,
                            is_open=False,
                            color='danger'
                        )
                    )
                ]),
                dbc.Textarea(
                    id='text-conversion-results',
                    className='string_input',
                    bs_size="lg",
                    readOnly=True,
                    style={'font-size': '16px', 'display': 'none'}
                ),
                dbc.Button(id='pause_loop', style={'display': 'none'}),
                dcc.Interval(id='interval-text-results', max_intervals=0, interval=500),
                html.Br(),
                html.Div(id='export-output', style={'display': 'none'}),
                html.Div(id='export-input', style={'display': 'none'}),
                dbc.Button(id='get_metadata_done', style={'display': 'none'}),
            ], style={'min-height': '110vh'})
        ]

        @self.parent_app.callback(
            [
                Output("popover_export_metadata", "is_open"),
                Output('alert_required', 'is_open'),
                Output('alert_required', 'children'),
            ],
            [Input('metadata-output-update-finished-verification', 'children')],
            [
                State("popover_export_metadata", "is_open"),
                State('alert_required', 'is_open')
            ]
        )
        def export_metadata(trigger, fileoption_is_open, req_is_open):
            """
            Export Metadata Form data to JSON and YAML file
            This function is triggered when metadata internal dict is updated
            and export controller is setted to true.
            If export controller is not setted to true but the metadata internal dict was updated
            the function will return the current application state
            """
            # Prevent default
            if not self.export_controller or not trigger:
                return fileoption_is_open, req_is_open, []

            if self.export_controller and fileoption_is_open:
                self.export_controller = False
                return not fileoption_is_open, req_is_open, []

            alerts, output = self.metadata_forms.data_to_nested()

            # If required fields missing return alert
            if alerts is not None:
                return fileoption_is_open, not req_is_open, alerts

            updated_data = dict_deep_update(self.start_metadata_data, output)

            # Make temporary files on server side
            # JSON
            exported_file_path = self.downloads_path / 'exported_metadata.json'
            with open(exported_file_path, 'w') as outfile:
                json.dump(updated_data, outfile, indent=4)

            # YAML
            exported_file_path = self.downloads_path / 'exported_metadata.yaml'
            with open(exported_file_path, 'w') as outfile:
                yaml.dump(updated_data, outfile, default_flow_style=False)

            return not fileoption_is_open, req_is_open, []

        @self.parent_app.callback(
            [
                Output('metadata-external-trigger-update-internal-dict', 'children'),
                Output('conversiondata-external-trigger-update-internal-dict', 'children')
            ],
            [
                Input('button_export_metadata', 'n_clicks'),
                Input('button_run_conversion', 'n_clicks')
            ],
        )
        def update_internal_metadata(click_export, click_conversion):
            """
            Trigger metadata internal dict update and then:
            1) set export_controller to true, when exporting to json/yaml
            2) set convert_controller to true, when running conversion
            """
            ctx = dash.callback_context
            if not ctx.triggered:
                return dash.no_update
            else:
                button_id = ctx.triggered[0]['prop_id'].split('.')[0]
                if button_id == 'button_export_metadata':
                    self.export_controller = True
                    self.convert_controller = False
                elif button_id == 'button_run_conversion':
                    self.export_controller = False
                    self.convert_controller = True
                return str(np.random.rand()), str(np.random.rand())

        @self.parent_app.callback(
            [
                Output('metadata-col', 'children'),
                Output('button_load_metadata', 'style'),
                Output('button_export_metadata', 'style'),
                Output('button_refresh', 'style'),
                Output('row_output_conversion', 'style'),
                Output('text-conversion-results', 'style'),
                Output('get_metadata_done', 'n_clicks'),
                Output('alert_required_source', 'is_open'),
                Output('alert_required_source', 'children'),
                Output('conversion-col', 'style')
            ],
            [Input('sourcedata-output-update-finished-verification', 'children')],
            [
                State('alert_required_source', 'is_open'),
                State('button_load_metadata', 'style'),
                State('button_export_metadata', 'style'),
                State('button_refresh', 'style'),
                State('row_output_conversion', 'style'),
                State('text-conversion-results', 'style'),
                State('conversion-col', 'style')
            ]
        )
        def get_metadata(trigger, alert_is_open, *styles):
            """
            Render Metadata forms based on Source Data Form
            This function is triggered when sourcedata internal dict is updated
            and get metadata controller is setted to true.
            If get metadata controller is not setted to true but the sourcedata
            internal dict was updated the function will return the current
            application state
            """
            if not trigger or not self.get_metadata_controller:
                # If metadata forms defined reset to default state
                if self.metadata_forms.children_forms:
                    self.metadata_forms.children_forms = []
                    self.metadata_forms.children = self.metadata_forms.children_triggers
                    self.metadata_forms.data = dict()
                    self.metadata_forms.schema = dict()
                return [self.metadata_forms, styles[0], styles[1], styles[2], styles[3], styles[4], None, alert_is_open, [], styles[5]]

            # Get forms data
            alerts, source_data = self.source_forms.data_to_nested()

            if alerts is not None:
                return [self.metadata_forms, styles[0], styles[1], styles[2], styles[3], styles[4], None, True, alerts, styles[5]]

            self.get_metadata_controller = False

            # Get metadata schema from converter
            self.converter = self.converter_class(source_data=source_data)
            self.metadata_json_schema = self.converter.get_metadata_schema()

            # Get metadata data from converter
            self.metadata_json_data = self.converter.get_metadata()
            self.start_metadata_data = self.metadata_json_data

            if self.metadata_forms.children_forms:
                # Clean form children if exists to render new one
                self.metadata_forms.children_forms = []

            self.metadata_forms.schema = self.metadata_json_schema
            self.metadata_forms.construct_children_forms()

            output_form = dbc.Card([
                dbc.Col(
                    html.H4('Metadata'),
                    style={'text-align': 'center', 'justify-content': 'center', "margin-top": "15px"},
                    width={'size': 12}
                ),
                dbc.CardBody(self.metadata_forms)
            ], style={'background-color': '##eceef7', "box-shadow": "2px 2px 2px 2px rgba(0,0,0,0.1)"})

            self.conversion_options_data = self.converter.get_conversion_options()

            try:
                self.metadata_forms.update_data(data=self.metadata_json_data)
                self.conversion_options_forms.update_data(data=self.conversion_options_data)
            except Exception as e:
                alert_field = ' '.join([w for w in str(e).strip().split('-')[1:] if not w.isdigit()])
                if alert_field == '':
                    alert_field = "One or more form fields failed to auto-fill. Please check if your Converter's metadata complies to its schema."
                exception_alert = [
                    html.H4('Field not found on schema', className='alert-heading'),
                    html.Hr(),
                    html.A(
                        alert_field,
                        href="#" + f'wrapper-{alert_field}',
                        className="alert-link"
                    )
                ]
                return [output_form, {'display': 'block'}, {'display': 'block'}, 
                {'display': 'block'}, {'display': 'block', 'text-align': 'left', 'margin-top': '15px'}, {'font-size': '16px', 'display': 'block', 'height': '100%', "min-height": "200px", "max-height": "600px"},
                1, True, exception_alert, {'display': 'block', "margin-top": "15px"}]

            return [
                output_form, {'display': 'block'}, {'display': 'block'},
                {'display': 'block'}, {'display': 'block', 'text-align': 'left', 'margin-top': '15px'}, {'font-size': '16px', 'display': 'block', 'height': '100%', "min-height": "200px", "max-height": "600px"},
                1, alert_is_open, [], {'display': 'block', "margin-top": "15px"}
            ]

        @self.parent_app.callback(
            Output('sourcedata-external-trigger-update-internal-dict', 'children'),
            [Input('get_metadata_btn', 'n_clicks')]
        )
        def update_internal_sourcedata(click):
            """Update sourcedata internal dictionary to Get Metadata Forms from it"""
            if click:
                self.get_metadata_controller = True
                return str(np.random.rand())

        @self.parent_app.callback(
            Output({'type': 'external-trigger-update-links-values', 'index': 'metadata-external-trigger-update-links-values'}, 'children'),
            [Input('button_refresh', 'n_clicks')]
        )
        def refresh_forms_links(click):

            if click:
                return str(np.random.rand())

            raise dash.exceptions.PreventUpdate

        @self.parent_app.callback(
            Output({'type': 'external-trigger-update-forms-values', 'index': 'metadata-external-trigger-update-forms-values'}, 'children'),
            [
                Input('button_load_metadata', 'contents'),
                Input('get_metadata_done', 'n_clicks')
            ],
            [State('button_load_metadata', 'filename')]
        )
        def update_forms_values_metadata(contents, click, filename):
            """
            Updates forms values (except links) when:
            - Forms are created (receives metadata dict from Converter)
            - User uploads metadata json / yaml file
            """
            ctx = dash.callback_context
            trigger_source = ctx.triggered[0]['prop_id'].split('.')[0]

            if trigger_source != 'button_load_metadata' and click is None:
                output = []
                return output

            if trigger_source != 'button_load_metadata' and click is not None:
                output = str(np.random.rand())
                return output

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

        @self.parent_app.server.route('/downloads/<path:filename>')
        def download_file(filename):
            return flask.send_from_directory(
                directory=self.downloads_path,
                path=filename,
                as_attachment=True,
            )

        @self.parent_app.callback(
            [
                Output('interval-text-results', 'max_intervals'),
                Output('alert-required-conversion', 'is_open'),
                Output('alert-required-conversion', 'children'),
            ],
            [
                Input('metadata-output-update-finished-verification', 'children'),
                Input('pause_loop', 'n_clicks')
            ],
            [
                State('output-nwbfile-name', 'value'),
                State('alert-required-conversion', 'is_open')
            ]
        )
        def trigger_conversion(trigger, pause, output_nwbfile, alert_is_open):
            ctx = dash.callback_context
            trigger_source = ctx.triggered[0]['prop_id'].split('.')[0]

            if trigger_source == 'metadata-output-update-finished-verification' and self.convert_controller:
                # run conversion
                alerts, metadata_form_data = self.metadata_forms.data_to_nested()

                _, conversion_options_data = self.conversion_options_forms.data_to_nested() # use this metadata to conversion

                metadata = dict_deep_update(self.start_metadata_data, metadata_form_data)

                if alerts is not None:
                    return 0, True, alerts

                nwbfile_path = output_nwbfile

                self.msg_buffer.truncate(0)

                self.t = threading.Thread(target=self.conversion, daemon=True, args=(metadata, nwbfile_path, conversion_options_data))
                self.t.start()

                self.conversion_msg_controller = True
                return -1, False, [] # run loop

            elif trigger_source == 'pause_loop' and pause is not None:
                # Pause interval component that reads conversion messages and terminate conversion thread
                if self.t.is_alive():
                    self.t.terminate()
                return 0, False, []

            return dash.no_update

        @self.parent_app.callback(
            [
                Output('text-conversion-results', 'value'),
                Output('pause_loop', 'n_clicks')
            ],
            [
                Input('interval-text-results', 'n_intervals')
            ]
        )
        def update_conversion_messages(n_intervals):
            self.conversion_messages = self.msg_buffer.getvalue()

            if self.conversion_msg_controller:
                return self.conversion_messages, None
            return self.conversion_messages, 1

    def conversion(self, metadata, nwbfile_path, conversion_options):
        try:
            with redirect_stdout(self.msg_buffer):
                self.converter.run_conversion(
                    metadata=metadata,
                    nwbfile_path=nwbfile_path,
                    save_to_file=True,
                    conversion_options=conversion_options
                )
        except Exception as e:
            self.msg_buffer.write(str(e))
        finally:
            time.sleep(0.1)
            self.convert_controller = False
            self.conversion_msg_controller = False
