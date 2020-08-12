import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import base64
import json
from pathlib import Path
import datetime


################################################################################
# THIS SHOULD BE REMOVED FORM HERE ONCE A FORMS CREATING FUNCTION IS IS PLACE
################################################################################
# Load JSON schema


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

            dcc.Upload(
                id="upload_schema",
                children=html.Div(
                    ["Drag and drop or click to select a file to upload."]
                ),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
                multiple=False,
            ),
            html.Br(),
            html.Div(id='uploaded_input_schema'),
            html.Br(),

            html.Div(id='forms_div'),
        ])

        self.style ={'text-align': 'center', 'justify-content': 'left'}

        @self.parent_app.callback(
            [Output("uploaded_input_schema", "children"), Output('forms_div', 'children')],
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
                    forms = iter_fields(json_schema)
                    layout_children = [
                        html.H1(
                            "Conversion Forms",
                            style={'text-align': 'center'}
                        ),
                        html.Hr(),
                    ]
                    layout_children.extend([f for f in forms])

                    all_forms = html.Div(layout_children)

                    return 'JSON schema loaded', all_forms
                else:
                    return 'Something went wrong'
            else:
                return '', ''

