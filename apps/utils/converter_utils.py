import dash_core_components as dcc
import dash_bootstrap_components as dbc
import base64
import datetime


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
