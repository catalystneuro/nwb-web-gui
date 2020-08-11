import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from base64 import b64decode
import json


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Load JSON schema
with open('apps/uploads/formData/NWBFile_form0.json') as json_file:
    metadata = json.load(json_file)


class FormItem(dbc.FormGroup):
    def __init__(self, key, value):
        super().__init__([])
        self.row = True
        self.children = [
            dbc.Col(
                dbc.Label(key, html_for="example-email-row", width=2),
                width=10,
            ),
            dbc.Col(
                dbc.Input(type="", id="example-email-row"),
                width=10,
            ),
        ]


def iter_fields(object):
    """Recursively iterate over items in schema to assemble form"""
    children = []
    for k, v in object.items():
        if v['type'] == 'object':
            item = html.Div(id="form_group_" + k)
            item.children = iter_fields(v['properties'])
        elif v['type'] == 'string':
            print(v)
            item = FormItem(key=k, value=v)
            print(item)
        children.append(item)


# App layout
form = iter_fields(metadata)
app.layout = html.Div([
    html.H1(
        "Conversion Forms",
        style={'text-align': 'center'}
    ),
    html.Hr(),

    form
])

print(form)

# @app.callback(dash.dependencies.Output('page-content', 'children'),
#               [dash.dependencies.Input('url', 'pathname')])
# def display_page(pathname):
#     return html.Div([
#         html.H3('You are on page {}'.format(pathname))
#     ])


if __name__ == '__main__':
    app.run_server(debug=True)
