import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import base64
import json
import datetime
from .utils.converter_utils import iter_fields, format_schema


class ConverterForms(html.Div):
    def __init__(self, parent_app):
        super().__init__([])
        self.parent_app = parent_app

        # Converter page layout
        self.children = html.Div([
            html.H2('Converter Forms', style={'text-align': 'center', 'margin-top': '15px'}),
            html.Br(),
            dbc.Container([
                dbc.Row(
                    [dbc.Col([
                        dcc.Upload(
                            id="upload_schema",
                            children=html.Div(
                                ["Drag and drop or click to select a file to upload."],
                            ),
                            style={
                                "width": "100%",
                                "height": "60px",
                                "lineHeight": "60px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                            },
                            multiple=False,
                        ),
                    ], className='col-md-4')],
                    style={'justify-content': 'center'}
            )]),
            html.Br(),
            html.Div(id='uploaded_input_schema'),
            html.Br(),
            dbc.Container([
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(id='forms_div'),
                            ],
                            className='col-md-12'
                        )
                    ])
            ], fluid=True),
            html.Br(),
            html.Div(id='forms_button'),
            html.Div(id='noDiv'),
        ])

        self.style = {'text-align': 'center', 'justify-content': 'left'}

        self.forms_ids = ['']

        @self.parent_app.callback(
            [Output("uploaded_input_schema", "children"), Output('forms_div', 'children'), Output('forms_button', 'children')],
            [Input("upload_schema", "contents")],
        )
        def load_metadata(contents):
            ctx = dash.callback_context
            source = ctx.triggered[0]['prop_id'].split('.')[0]

            if source == 'upload_schema':
                if isinstance(contents, str):
                    content_type, content_string = contents.split(',')
                    bs4decode = base64.b64decode(content_string)
                    json_string = bs4decode.decode('utf8').replace("'", '"')
                    json_schema = json.loads(json_string)
                    self.uploaded_schema = json_schema
                    forms = iter_fields(json_schema, set_counter=True)
                    tabs = [dbc.Tab(e, label=e.children[0].children) for i, e in enumerate(forms)]

                    from .utils.converter_utils import forms_ids  # returning on iter_fields is breaking the recursion stack *check this*

                    self.forms_ids = forms_ids

                    layout_children = [
                        html.H1(
                            "Conversion Forms",
                            style={'text-align': 'center'}
                        ),
                        html.Hr(),
                        dbc.Tabs(tabs)
                    ]

                    all_forms = html.Div(layout_children)

                    button = dbc.Button('Submit', id='button_submit')

                    return 'JSON schema loaded', all_forms, button
                else:
                    return 'Something went wrong', '', ''
            else:
                return '', '', ''

        @self.parent_app.callback(
            Output('noDiv', 'children'),
            [Input('button_submit', component_property='n_clicks')],
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
