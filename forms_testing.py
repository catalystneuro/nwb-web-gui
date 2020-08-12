import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from base64 import b64decode
import datetime
import json


external_stylesheets = [dbc.themes.BOOTSTRAP]  # ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

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


# App layout
forms = iter_fields(metadata)
layout_children = [
    html.H1(
        "Conversion Forms",
        style={'text-align': 'center'}
    ),
    html.Hr(),
]
layout_children.extend([f for f in forms])
app.layout = html.Div(layout_children)

# @app.callback(dash.dependencies.Output('page-content', 'children'),
#               [dash.dependencies.Input('url', 'pathname')])
# def display_page(pathname):
#     return html.Div([
#         html.H3('You are on page {}'.format(pathname))
#     ])


if __name__ == '__main__':
    app.run_server(debug=True)
