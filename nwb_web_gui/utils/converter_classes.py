import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import datetime
import dash_daq as daq
from date_time_picker import DateTimePicker


class FormItem(dbc.FormGroup):
    """Custom form group instance"""

    def __init__(self, label, form_input, parent_app, label_id, input_id):
        super().__init__([])

        self.parent_app = parent_app
        self.className = 'item'

        if 'source_data' in input_id or 'conversion_options' in input_id:
            self.children = dbc.Row([
                dbc.Col(
                    label,
                    width={'size': 4, 'offset': 0}
                ),
                dbc.Col(
                    form_input,
                    width={'size': 8, 'offset': 0}
                )
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

        '''
        @self.parent_app.callback(
            State(input_id, "value")
        )
        def get_form_value(input_value):
            print(input_value)
        '''


class SingleForm(dbc.Form):
    """Single form instance"""

    def __init__(self, value, base_schema, parent_app, item_name):
        super().__init__([])

        required_fields = base_schema['required']
        children = []

        self.id = item_name
        item_name = item_name.replace(' ', '_').lower()

        for schema_k, schema_v in base_schema['properties'].items():
            if schema_k in value.keys():
                label_id = f'label_{item_name}_{schema_k}'
                input_id = f'input_{item_name}_{schema_k}'
                hidden_id = f'hidden_{item_name}_{schema_k}'
                if 'format' in schema_v and schema_v['format'] == 'date-time':
                    form_input = DateTimePicker(
                        id=input_id,
                        value=value[schema_k],
                        style={"border": "solid 1px", "border-color": "#ced4da", "border-radius": "5px", "color": '#545057'}
                    )
                elif schema_v['type'] == 'string':
                    form_input = dbc.Input(
                        value=value[schema_k],
                        id=input_id,
                        className='string_input'
                    )
                elif schema_v['type'] == 'boolean':
                    form_input = dbc.Checkbox(
                        id=input_id, className="form-check-input"
                    ),

                label = dbc.Label(schema_k, id=label_id)

                form_group = FormItem(
                    label,
                    form_input,
                    parent_app=parent_app,
                    label_id=label_id,
                    input_id=input_id
                )
                children.append(form_group)

        self.children = html.Div(children, style={'margin-top': '5px'})


class CompositeForm(html.Div):
    """ Composite form instance """

    def __init__(self, value, key, base_schema, parent_app, parent_name):
        super().__init__([])

        self.parent_name = parent_name  # Ecephys, ophys etc
        self.id = parent_name

        tabs = []

        for i, e in enumerate(value):
            tab_title = f'{key}_{i}'
            children = []
            for k, v in e.items():
                input_id = f'input_{parent_name}_{k}_{i}'
                label_id = f'label_{parent_name}_{k}_{i}'

                if k in base_schema['properties'].keys():
                    if isinstance(v, str) or isinstance(v, float) or isinstance(v, int):
                        form_input = dbc.Input(value=v, id=input_id, className='string_input')
                        label = dbc.Label(k, id=label_id)
                        form_group = FormItem(label, form_input, parent_app=parent_app, label_id=label_id, input_id=input_id)
                        children.append(form_group)
                    elif isinstance(v, dict):
                        label = dbc.Label(k, id=label_id)
                        form_input = dcc.Dropdown(
                            id=input_id,
                            options=[
                                {'label': 'Device 1', 'value': 'dev1'},
                                {'label': 'Device 2', 'value': 'dev2'},
                                {'label': 'Device 3', 'value': 'dev3'}
                            ],
                            value='dev1',
                            clearable=False,
                            className='dropdown_input',
                            style={"margin-bottom": '20px'}
                        )
                        form_group = FormItem(label, form_input, parent_app=parent_app, label_id=label_id, input_id=input_id)
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
                                form_group = FormItem(label, form_input, parent_app=parent_app, label_id=label_id, input_id=input_id)
                                optical_children.append(form_group)

                            form = dbc.Form(optical_children, style={'margin-top': '5px'})
                            tab = dbc.Tab(form, label='Optical_Channel_{}'.format(index), tab_style={'background-color': '#f7f7f7', 'border':'solid', 'border-color': '#f7f7f7', 'border-width': '1px'})
                            optical_tabs.append(tab)

                        optical_tab = dbc.Tabs(optical_tabs)
                        children.append(optical_tab)

            form = dbc.Form(children, style={'margin-top':'5px'})
            tab = dbc.Tab(form, label=tab_title, tab_style={'background-color': '#f7f7f7', 'border':'solid', 'border-color': '#f7f7f7', 'border-width': '1px'})
            tabs.append(tab)

        self.children = dbc.Tabs(tabs)
        self.style={'margin-top': '5px'}
