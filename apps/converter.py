import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from base64 import b64decode
import json
from pathlib import Path


class ConverterForms(html.Div):
    def __init__(self, parent_app):
        super().__init__([])
        self.parent_app = parent_app

        # Converter page layout
        self.children = html.Div([
            html.H2('Converter Forms', style={'text-align': 'center'}),
            html.Br(),

            dcc.Upload(id="input_schema", children=html.A('Input JSON File')),
            dcc.Input(id="uploaded_input_schema", type='text'),
            html.Br(),

            dcc.Upload(id="metadata_schema", children=html.A('Metadata JSON File')),
            html.Br(),

            html.Div(
                [
                    dbc.Row([
                        dbc.Col([
                            dbc.Form(
                            [
                                dbc.FormGroup(
                                    [
                                        dbc.Label("Path to local metadata JSON schema"),
                                        dbc.Input(type="text", id='local_metadata', placeholder="Path/to/metadata.json"),
                                    ],
                                ),
                                dbc.Button('Submit', id='submit_metadata'),
                            ],
                        )
                        ], className='col-md-6'),
                    ], style={'align-items':'center', 'justify-content':'center', 'text-align':'center'})
                ]
            ),
            html.Div(id='my-output'),
            html.Div(id='converter-content'),
            html.Br(),

        ])

        self.style ={'text-align': 'center', 'justify-content':'center'}


        @self.parent_app.callback(
            Output("uploaded_input_schema", "children"),
            [Input("input_schema", "contents")],
        )
        def load_input_schema(contents):

            dc = b64decode(contents.split(',')[1]).decode()
            input_schema = json.loads(dc)
            for k, v in data.items():
                print(k)

            return 'JSON schema loaded'


        @self.parent_app.callback(
            Output('my-output', 'children'),
            [Input("submit_metadata", component_property='n_clicks'),
            Input('local_metadata', component_property='value')]
        )
        def submit_local_schema(click, input_value):
            if click is not None:
                metadata_path = Path(input_value)

                if not metadata_path.is_file():
                    return 'Must be a JSON'
                else:
                    with open(metadata_path, 'r') as inp:
                        schema = json.load(inp)

                    return ('JSON schema loaded')
