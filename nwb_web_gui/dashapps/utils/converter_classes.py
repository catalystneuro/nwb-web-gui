import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import datetime
import dash_daq as daq
from date_time_picker import DateTimePicker


class FormItem(dbc.FormGroup):
    """Custom form group instance"""

    def __init__(self, label, form_input, label_id, input_id, add_explorer=False, source=False):
        super().__init__([])

        self.className = 'item'

        if add_explorer:
            explorer = dbc.Button(id={'name': 'source_explorer', 'index': input_id.replace('input', 'explorer')}, children=[html.I(className="far fa-folder")], style={'background-color': 'transparent', 'color': 'black', 'border': 'none'})
        else:
            explorer = ''

        if source:
            self.children = dbc.Row([
                dbc.Col(
                    label,
                    width={'size': 4, 'offset': 0}
                ),
                dbc.Col([
                        form_input
                    ],
                    width={'size': 6, 'offset': 0}
                ),
                dbc.Col([explorer], width={'size': 1})
            ])
        else:
            self.children = dbc.Row([
                dbc.Col(
                    label,
                    width={'size': 2, 'offset': 0}
                ),
                dbc.Col(
                    form_input,
                    width={'size': 10, 'offset': 0}
                )
            ])


class SourceForm(dbc.Form):
    def __init__(self, value, base_schema, item_name):
        super().__init__([])

        required = base_schema['required']
        children = []
        prefix = 'source'

        self.id = item_name

        base_properties = base_schema['items']['properties']

        for e in value:
            for schema_k, schema_v in base_properties.items():
                if schema_k in e:
                    if schema_k == 'name':
                        name = e[schema_k]
                        label_id = f'label_{item_name}_{e[schema_k]}'
                        label = dbc.Label(e[schema_k], id=label_id)
                    else:
                        if schema_v['type'] == 'string' and schema_k != 'type':
                            input_id = f'input_{item_name}_{name}_{schema_k}'
                            form_input = dbc.Input(
                                value=e[schema_k],
                                id={'name': f'{prefix}-string-input', 'index': input_id},
                                className='string_input',
                                type='input'
                            )
                            add_explorer = True

                        elif schema_v['type'] == 'boolean' and schema_k !='type':
                            input_id = f'input_{item_name}_{name}_{schema_k}'
                            form_input = dbc.Checkbox(
                                id={'name': f'{prefix}-boolean-input', 'index':input_id}, className="form-check-input"
                            )
                            add_explorer = False

                        if schema_k != 'type':
                            form_group = FormItem(
                                label,
                                form_input,
                                label_id=label_id,
                                input_id=input_id,
                                add_explorer=add_explorer,
                                source=True
                            )

                            children.append(form_group)

        self.children = html.Div(children, style={'margin-top': '5px'})


class SingleForm(dbc.Form):
    """Single form instance"""

    def __init__(self, value, base_schema, item_name):
        super().__init__([])

        required_fields = base_schema['required']
        children = []

        prefix = 'metadata'

        self.id = item_name
        item_name = item_name.replace(' ', '_').lower()

        for schema_k, schema_v in base_schema['properties'].items():
            if schema_k in value.keys():
                label_id = f'label_{item_name}_{schema_k}'
                input_id = f'input_{item_name}_{schema_k}'
                hidden_id = f'hidden_{item_name}_{schema_k}'
                if 'format' in schema_v and schema_v['format'] == 'date-time':
                    form_input = DateTimePicker(
                        id={'name': f'{prefix}-date-input', 'index': input_id},
                        value=value[schema_k],
                        style={"border": "solid 1px", "border-color": "#ced4da", "border-radius": "5px", "color": '#545057'}
                    )
                    add_explorer = False
                elif schema_v['type'] == 'string':
                    if isinstance(value[schema_k], dict):
                        default = value[schema_k]['path']
                        add_explorer = True
                    else:
                        default = value[schema_k]
                        add_explorer = False
                    form_input = dbc.Input(
                        value=default,
                        id={'name': f'{prefix}-string-input', 'index': input_id},
                        className='string_input',
                        type='input'
                    )
                elif schema_v['type'] == 'boolean':
                    form_input = dbc.Checkbox(
                        id={'name': f'{prefix}-boolean-input', 'index':input_id}, className="form-check-input"
                    )
                    add_explorer = False

                label = dbc.Label(schema_k, id=label_id)

                form_group = FormItem(
                    label,
                    form_input,
                    label_id=label_id,
                    input_id=input_id,
                    add_explorer=add_explorer
                )
                children.append(form_group)

        self.children = html.Div(children, style={'margin-top': '5px'})


class CompositeForm(html.Div):
    """ Composite form instance """

    def __init__(self, value, key, base_schema, parent_name, devices_list=[]):
        super().__init__([])

        self.parent_name = parent_name  # Ecephys, ophys etc
        self.id = parent_name
        self.devices_list = devices_list

        tabs = []

        for i, e in enumerate(value):
            tab_title = f'{key}_{i}'
            children = []
            if key == 'Device':
                self.devices_list.append({'label': e['name'], 'value': e['name']})
            for k, v in e.items():
                input_id = f'input_{parent_name}_{k}_{i}'
                label_id = f'label_{parent_name}_{k}_{i}'

                if k in base_schema['properties'].keys():
                    if isinstance(v, str) or isinstance(v, float) or isinstance(v, int):
                        form_input = dbc.Input(value=v, id=input_id, className='string_input')
                        label = dbc.Label(k, id=label_id)
                        form_group = FormItem(label, form_input, label_id=label_id, input_id=input_id)
                        children.append(form_group)
                    elif isinstance(v, dict):
                        label = dbc.Label(k, id=label_id)
                        form_input = dcc.Dropdown(
                            id=input_id,
                            options=self.devices_list,
                            value=v['target'],
                            clearable=False,
                            className='dropdown_input',
                            style={"margin-bottom": '20px'}
                        )
                        form_group = FormItem(label, form_input, label_id=label_id, input_id=input_id)
                        children.append(form_group)
                    elif isinstance(v, list):
                        optical_tabs = []
                        for index, element in enumerate(v):
                            optical_children = []
                            for key_optical, val in element.items():
                                input_id = f'input_{parent_name}_{k}_{key_optical}_{index}'
                                label_id = f'label_{parent_name}_{k}_{key_optical}_{index}'
                                form_input = dbc.Input(value=val, id=input_id, className='string_input')
                                label = dbc.Label(key_optical, id=label_id)
                                form_group = FormItem(label, form_input, label_id=label_id, input_id=input_id)
                                optical_children.append(form_group)

                            form = dbc.Form(optical_children, style={'margin-top': '5px'})
                            optical_card = dbc.Card(
                                [
                                    dbc.CardBody(form)
                                ]
                            )

                            optical_div = dbc.Row([
                                dbc.Col(f'{k}', md=2, style={'justify-content': 'left', 'text-align': 'left'}),
                                dbc.Col(optical_card, md=10)
                            ])
                            children.append(optical_div)

            form = dbc.Form(children, style={'margin-top':'5px'})
            tab = dbc.Tab(form, label=tab_title, tab_style={'background-color': '#f7f7f7', 'border':'solid', 'border-color': '#f7f7f7', 'border-width': '1px'})
            tabs.append(tab)

        self.children = dbc.Tabs(tabs)
        self.style={'margin-top': '5px'}
