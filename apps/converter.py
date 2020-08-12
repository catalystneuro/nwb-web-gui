import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from base64 import b64decode
import json
from pathlib import Path
import datetime


################################################################################
# THIS SHOULD BE REMOVED FORM HERE ONCE A FORMS CREATING FUNCTION IS IS PLACE
################################################################################
# Load JSON schema
with open('apps/uploads/formData/NWBFile_form0.json') as json_file:
    metadata = json.load(json_file)


class FormItem(dbc.FormGroup):
    def __init__(self, key, value, type):
        super().__init__([])
        self.row = True
        if type == 'string':
            input_field = dbc.Input(type="")
        elif type == 'datetime':
            input_field = dcc.DatePickerSingle(
                month_format='MMMM Y',
                placeholder='MMMM Y',
                date=datetime.date(2020, 2, 29)
            )
        elif type == 'link':
            input_field = dcc.Dropdown(
                id='dropdown-' + key,
                options=[
                    {'label': 'Device 1', 'value': 'dev1'},
                    {'label': 'Device 2', 'value': 'dev2'},
                    {'label': 'Device 3', 'value': 'dev3'}
                ],
                value='dev1',
                clearable=False
            )
        else:
            input_field = dbc.Input(type="")
        self.children = [
            dbc.Label(key, html_for="example-email-row", width={'size': 2, 'offset': 1}),
            dbc.Col(
                input_field,
                width={'size': 3, 'offset': 0},
            ),
        ]


def iter_fields(object):
    """Recursively iterate over items in schema to assemble form"""
    children = []
    for k, v in object.items():
        if v['type'] == 'object':
            # item = html.Div(id="form_group_" + k, style={"border": "1px black solid"})
            item = dbc.Card(id="form_group_" + k)
            item.children = [dbc.CardHeader(k)]
            item.children.extend(iter_fields(v['properties']))
            children.append(item)
        # elif v['type'] == 'string':
        else:
            item = FormItem(key=k, value=v, type=v['type'])
            children.append(item)
        # else:
        #     # we were getting duplicate values ​​because we have to treat all types of fields (and give a unique id for each input?)
        #     pass
    return children


forms = iter_fields(metadata)
layout_children = [
    html.H1(
        "Conversion Forms",
        style={'text-align': 'center'}
    ),
    html.Hr(),
]
layout_children.extend([f for f in forms])
all_forms = html.Div(layout_children)
################################################################################
################################################################################


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
                    ], style={'align-items': 'center', 'justify-content': 'center', 'text-align':'center'})
                ]
            ),
            html.Div(id='my-output'),
            html.Div(id='converter-content'),
            html.Br(),

            all_forms
        ])

        self.style ={'text-align': 'center', 'justify-content':'left'}


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
