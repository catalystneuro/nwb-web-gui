import dash_core_components as dcc
import dash_bootstrap_components as dbc
import base64
import datetime


counter = 0


class FormItem(dbc.FormGroup):
    def __init__(self, key, value, type, input_id):
        super().__init__([])

        self.row = True
        if type == 'string':
            if 'format' in value and value['format'] == 'date-time':
                input_field = dcc.DatePickerSingle(
                    month_format='MMMM Y',
                    placeholder='MMMM Y',
                    date=datetime.date(2020, 2, 29),
                    id=str(input_id)
                )
            else:
                input_field = dbc.Input(type="", id=str(input_id))
        elif type == 'link':
            input_field = dcc.Dropdown(
                id=str(input_id),
                options=[
                    {'label': 'Device 1', 'value': 'dev1'},
                    {'label': 'Device 2', 'value': 'dev2'},
                    {'label': 'Device 3', 'value': 'dev3'}
                ],
                value='dev1',
                clearable=False
            )
        elif type == 'boolean':
            input_field = dbc.FormGroup(
                [
                    dbc.Checklist(
                        options=[
                            {"label": "", "value": key},
                        ],
                        value=[],
                        id=str(input_id),
                    ),
                ]
            )
        else:
            input_field = dbc.Input(type="", id=str(input_id))
        self.children = [
            dbc.Label(key, html_for="example-email-row", width={'size': 2, 'offset': 1}),
            dbc.Col(
                input_field,
                width={'size': 3, 'offset': 0},
            ),
        ]


def iter_fields(object, ids_list=[], set_counter=False):
    """Recursively iterate over items in schema to assemble form"""
    children = []
    global counter

    if set_counter:
        counter = 0
        ids_list = []

    for k, v in object.items():
        if v['type'] == 'object':
            # item = html.Div(id="form_group_" + k, style={"border": "1px black solid"})
            item = dbc.Card(id="form_group_" + k, style={'margin-bottom': '20px', 'box-shadow': '6px 6px 6px rgba(0, 0, 0, 0.2)'})
            item.children = [dbc.CardHeader(k, style={'margin-bottom': '10px'})]
            item.children.extend(iter_fields(v['properties'], ids_list))
            children.append(item)
        else:
            item = FormItem(key=k, value=v, type=v['type'], input_id=counter)
            counter += 1
            ids_list.append(counter)
            children.append(item)
        # else:
        #     # we were getting duplicate values ​​because we have to treat all types of fields (and give a unique id for each input?)
        #     pass

    return children
