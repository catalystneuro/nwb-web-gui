import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import base64
import json
import datetime
from .utils.converter_utils import iter_fields, format_schema, instance_to_forms
from .utils.utils import get_form_from_metadata, edit_output_form
from .utils.file_picker import make_upload_file, make_json_file_buttons


class ConverterForms(html.Div):
    def __init__(self, parent_app):
        super().__init__([])
        self.parent_app = parent_app
        self.metadata_forms = ''
        self.input_forms = ''
        self.conversion_button = ''
        self.source_json = ''
        self.metadata_json = ''

        json_buttons_source = make_json_file_buttons(id_suffix='source')
        json_buttons_metadata = make_json_file_buttons(id_suffix='metadata')

        self.children = dbc.Container([
            html.Br(),
            html.H1("NWB Converter", style={'text-align': 'center'}),
            dbc.Label(id='warnings', color='danger'),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    html.H3('Source data'),
                    json_buttons_source,
                    html.Hr(),
                    html.Div(id='source_data_div'),
                ], lg=4),
                dbc.Col([
                    html.H3('Metadata'),
                    json_buttons_metadata,
                    html.Hr(),
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
            html.Div(style={'display':'none'}, id='hidden_div')
        ], fluid=True)

        self.style = {'text-align': 'center', 'justify-content': 'left'}

        self.forms_ids = ['']

        @self.parent_app.callback(
            [
                Output('metadata_forms_div', 'children'),
                Output('source_data_div', 'children'),
                Output('button_row', 'children'),
                Output('warnings', 'children')
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
                if isinstance(form_tabs, list):
                    return '', '', '', 'Something went wrong'

                layout_children = [
                    form_tabs
                ]
                self.metadata_forms = html.Div(layout_children)
                self.conversion_button = dbc.Button('Run conversion', id='button_run_conversion')

                return self.metadata_forms, self.input_forms, self.conversion_button, ''

            elif source == 'load_json_source':
                self.source_json = data_json
                form_tabs = get_form_from_metadata(data_json, self.parent_app)
                if isinstance(form_tabs, list):
                    layout_children = []
                    layout_children.extend([f for f in form_tabs])
                    self.input_forms = html.Div(layout_children)
                    self.conversion_button = dbc.Button('Run conversion', id='button_run_conversion')

                    return self.metadata_forms, self.input_forms, self.conversion_button, ''
                else:
                    return '', '', '', 'Something went wrong'
            else:
                return '', '', '', ''




        '''
        @self.parent_app.callback(
            Output('hidden_div', 'children'),
            [Input('save_json_source', 'n_clicks')],
            [
                State({'name': 'source-string-input', 'index': ALL}, 'value'), State({'name': 'source-string-input', 'index': ALL}, 'id'),
                State({'name': 'source-boolean-input', 'index': ALL}, 'value'), State({'name': 'source-boolean-input', 'index': ALL}, 'id')

            ]
        )
        def send_source_forms(n_click, string_values, string_id, boolean_values, boolean_id):
            print(boolean_values, boolean_id)
            
            if len(string_id) > 0 and len(string_values) > 0:
                index_list = [e['index'].split('input_source_data_')[-1] for e in string_id]

                string_dict = {}
                for idx, value in zip(index_list, string_values):
                    string_dict[idx] = value

                string_dict['add_raw'] = True
                string_dict['add_processed'] = True
                string_dict['add_behavior'] = True
                
                output_form = edit_output_form(self.source_json, string_dict)
        

        @self.parent_app.callback(
            Output('hidden_div2', 'children'),
            [Input('save_json_metadata', 'n_clicks')]
        )
        def send_metadata_forms(n_click):
            pass
        '''

    def clean_converter_forms(self):
        self.metadata_forms = ''
        self.input_forms = ''
        self.conversion_button = ''
