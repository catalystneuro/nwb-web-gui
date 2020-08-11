import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

from base64 import b64decode
import json


class ConverterForms(html.Div):
    def __init__(self, parent_app):
        super().__init__([])
        self.parent_app = parent_app

        # Converter page layout
        self.children = html.Div([
            html.H2('Converter Forms'),
            html.Br(),

            dcc.Upload(id="input_schema", children=html.A('Input JSON File')),
            dcc.Input(id="uploaded_input_schema", type='text'),
            html.Br(),

            dcc.Upload(id="metadata_schema", children=html.A('Metadata JSON File')),
            html.Br(),

            html.Div(id='converter-content'),
            html.Br(),
        ])


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
