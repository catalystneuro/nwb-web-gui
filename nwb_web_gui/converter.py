import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import base64
import json
import datetime
from .utils.converter_utils import iter_fields, format_schema, instance_to_forms
from .utils.utils import get_form_from_metadata
from .utils.file_picker import make_upload_file, make_json_file_buttons


class ConverterForms(html.Div):
    def __init__(self, parent_app):
        super().__init__([])
        self.parent_app = parent_app
        self.metadata_forms = ''
        self.input_forms = ''
        self.conversion_button = ''

        json_buttons_source = make_json_file_buttons(id_suffix='source')
        json_buttons_metadata = make_json_file_buttons(id_suffix='metadata')

        self.children = dbc.Container([
            html.Br(),
            html.H1("NWB Converter", style={'text-align': 'center'}),
            html.Br(),
            html.Hr(),

            dbc.Label(id='warnings', color='danger'),
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
            )
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
                metadata_json = json.loads(json_string)

            if source == 'load_json_metadata':
                form_tabs = get_form_from_metadata(metadata_json, self.parent_app)
                if isinstance(form_tabs, list):
                    return '', '', '', 'Something went wrong'

                layout_children = [
                    form_tabs
                ]
                self.metadata_forms = html.Div(layout_children)
                self.conversion_button = dbc.Button('Run conversion', id='button_run_conversion')

                return self.metadata_forms, self.input_forms, self.conversion_button, ''

            elif source == 'load_json_source':
                form_tabs = get_form_from_metadata(metadata_json, self.parent_app)
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
            Output('noDiv', 'children'),
            [Input('button_run_conversion', component_property='n_clicks')],
            [State(f"{i}", "value") for i in range(0, 20)]  # states watch type for boolean fields must be "on" instead of "value" and for datetime object must be "date" instead of "value"
        )
        def submit_form(click, *args):

            form_data = {}
            if click is not None:
                for i, e in enumerate(args):
                    if e is not None:
                        form_key = '{}_{}'.format(self.forms_ids[i]['key'], self.forms_ids[i]['father_name'])
                        form_data[form_key] = e

                default_schema = format_schema(self.uploaded_schema, form_data)

                # Save new json shema (tests)
                with open('output_schema.json', 'w') as inp:
                    json.dump(default_schema, inp, indent=4)
        '''

    def clean_converter_forms(self):
        self.metadata_forms = ''
        self.input_forms = ''
        self.conversion_button = ''
