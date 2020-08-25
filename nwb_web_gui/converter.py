import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, ALL, MATCH
import dash_bootstrap_components as dbc
import base64
import json
import datetime
from nwb_web_gui.utils.utils import get_form_from_metadata, edit_output_form
from nwb_web_gui.utils.make_components import make_json_file_buttons, make_modal


class ConverterForms(html.Div):
    def __init__(self, parent_app):
        super().__init__([])
        self.parent_app = parent_app
        self.metadata_forms = ''
        self.input_forms = ''
        self.conversion_button = ''
        self.source_json = ''
        self.metadata_json = ''
        self.current_modal_source = ''

        json_buttons_source = make_json_file_buttons(id_suffix='source')
        json_buttons_metadata = make_json_file_buttons(id_suffix='metadata')
        modal = make_modal(parent_app)

        self.children = dbc.Container(
            [
                html.Br(),
                dbc.Label(id='warnings', color='danger'),
                dbc.Row([
                    dbc.Col([
                        html.H3('Source data'),
                        json_buttons_source,
                        html.Hr(),
                        dbc.Collapse(
                            dbc.Card(dbc.CardBody(
                                dcc.Textarea(
                                    id='textarea_json_source',
                                    disabled=True,
                                    style={'width': '100%', 'height': 300},
                                )
                            )),
                            id="collapse_json_source",
                        ),
                        html.Div(id='source_data_div'),
                    ], lg=4),
                    dbc.Col([
                        html.H3('Metadata'),
                        json_buttons_metadata,
                        html.Hr(),
                        dbc.Collapse(
                            dbc.Card(dbc.CardBody(
                                dcc.Textarea(
                                    id='textarea_json_metadata',
                                    disabled=True,
                                    style={'width': '100%', 'height': 300},
                                )
                            )),
                            id="collapse_json_metadata",
                        ),
                        html.Div(id='metadata_forms_div'),
                    ], lg=8)
                ]),
                html.Br(),
                dbc.Row(
                    dbc.Col(
                        id='button_row',
                        lg=12
                    )
                ),
                modal,
                html.Div(style={'display': 'none'}, id='hidden_div'),
                html.Br(),
                html.Div(id='hidden_tests')
            ],
            fluid=True
        )

        self.style = {'text-align': 'center', 'justify-content': 'left'}

        self.forms_ids = ['']

        @self.parent_app.callback(
            Output({'name': 'source-string-input', 'index': MATCH}, 'value'),
            [Input('submit_file_browser_modal', 'n_clicks')],
            [
                State('chosen_file_modal', 'value'),
                State({'name': 'source-string-input', 'index': MATCH}, 'value'),
                State({'name': 'source-string-input', 'index': MATCH}, 'id'),
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
            [
                Output('metadata_forms_div', 'children'),
                Output('source_data_div', 'children'),
                Output('button_row', 'children'),
                Output('warnings', 'children'),
                Output('textarea_json_metadata', 'value'),
                Output('textarea_json_source', 'value')
            ],
            [
                Input("load_json_source", "contents"),
                Input("load_json_metadata", "contents")
            ],
        )
        def load_metadata(*args):
            ctx = dash.callback_context
            source = ctx.triggered[0]['prop_id'].split('.')[0]
            contents = None

            if source == 'load_json_source':
                contents = args[0]
            elif source == 'load_json_metadata':
                contents = args[1]

            if isinstance(contents, str):
                content_type, content_string = contents.split(',')
                bs4decode = base64.b64decode(content_string)
                json_string = bs4decode.decode('utf8').replace("'", '"')
                data_json = json.loads(json_string)

            if source == 'load_json_metadata':
                self.metadata_json = data_json
                form_tabs = get_form_from_metadata(data_json, self.parent_app)

                if form_tabs is None:
                    return '', '', '', 'Something went wrong', '', ''

                layout_children = [
                    form_tabs
                ]
                self.metadata_forms = html.Div(layout_children)
                self.conversion_button = dbc.Button('Run conversion', id='button_run_conversion')

                return self.metadata_forms, self.input_forms, self.conversion_button, '', json.dumps(self.metadata_json, indent=4), json.dumps(self.source_json, indent=4)

            elif source == 'load_json_source':
                self.source_json = data_json
                form_tabs = get_form_from_metadata(data_json, self.parent_app, source=True)
                if isinstance(form_tabs, list):
                    layout_children = []
                    layout_children.extend([f for f in form_tabs])
                    self.input_forms = html.Div(layout_children)
                    self.conversion_button = dbc.Button('Run conversion', id='button_run_conversion')

                    return self.metadata_forms, self.input_forms, self.conversion_button, '', json.dumps(self.metadata_json, indent=4), json.dumps(self.source_json, indent=4)
                else:
                    return '', '', '', 'Something went wrong', '', ''
            else:
                return '', '', '', '', 'The JSON data for metadata will come here', 'The JSON data for source will come here'

        @self.parent_app.callback(
            Output('modal_explorer', 'is_open'),
            [Input({'name': 'source_explorer', 'index': ALL}, 'n_clicks'), Input('close_explorer_modal', 'n_clicks')],
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
            Output('hidden_div', 'children'),
            [Input('save_json_source', 'n_clicks')],
            [
                State({'name': 'source-string-input', 'index': ALL}, 'value'), State({'name': 'source-string-input', 'index': ALL}, 'id'),
                State({'name': 'source-boolean-input', 'index': ALL}, 'value'), State({'name': 'source-boolean-input', 'index': ALL}, 'id')

            ]
        )
        def send_source_forms(n_click, string_values, string_id, boolean_values, boolean_id):

            if len(string_id) > 0 and len(string_values) > 0:
                index_list = [e['index'].split('input_source_data_')[-1] for e in string_id]

                string_dict = {}
                for idx, value in zip(index_list, string_values):
                    string_dict[idx] = value

                # Value for test
                string_dict['add_raw'] = True
                string_dict['add_processed'] = True
                string_dict['add_behavior'] = True

                output_form = edit_output_form(self.source_json, string_dict)

                self.output_form = output_form

                with open('output_source.json', 'w') as output:
                    json.dump(self.output_form, output, indent=4)

        @self.parent_app.callback(
            Output('hidden_div2', 'children'),
            [Input('save_json_metadata', 'n_clicks')]
        )
        def send_metadata_forms(n_click):
            pass

        @self.parent_app.callback(
            Output("collapse_json_metadata", "is_open"),
            [Input("show_json_metadata", "n_clicks")],
            [State("collapse_json_metadata", "is_open")],
        )
        def toggle_collapse(n, is_open):
            if n:
                return not is_open
            return is_open

        @self.parent_app.callback(
            Output("collapse_json_source", "is_open"),
            [Input("show_json_source", "n_clicks")],
            [State("collapse_json_source", "is_open")],
        )
        def toggle_collapse(n, is_open):
            if n:
                return not is_open
            return is_open

    def clean_converter_forms(self):
        self.metadata_forms = ''
        self.input_forms = ''
        self.source_json = ''
        self.metadata_json = ''
        self.conversion_button = ''
