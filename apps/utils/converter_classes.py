import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import datetime


class FormItem(dbc.FormGroup):
    """Custom form group instance"""

    def __init__(self, label, form_input, parent_app, label_id, input_id):
        super().__init__([])

        self.parent_app = parent_app
        self.className = 'item'

        self.children = dbc.Row([
            dbc.Col(
                label,
                width={'size': 2, 'offset': 0}
            ),
            dbc.Col(
                form_input,
                width={'size': 3, 'offset': 0}
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

        for schema_k, schema_v in base_schema['properties'].items():
            if schema_k in value.keys():
                label_id = f'label_{item_name}_{schema_k}'
                input_id = f'input_{item_name}_{schema_k}'
                hidden_id = f'hidden_{item_name}_{schema_k}'
                if 'format' in schema_v and schema_v['format'] == 'date-time':
                    form_input = dcc.DatePickerSingle(
                        month_format='MMMM Y',
                        placeholder='MMMM Y',
                        date=datetime.date(2020, 2, 29),
                        className='date_input',
                        style={'font-size': '5px'},
                        id=input_id
                    )
                elif schema_v['type'] == 'string':
                    form_input = dbc.Input(
                        placeholder=value[schema_k],
                        id=input_id,
                        className='string_input'
                    )

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
                    if isinstance(v, str):
                        form_input = dbc.Input(placeholder=v, id=input_id, className='string_input')
                        label = dbc.Label(k, id=label_id)
                        form_group = FormItem(label, form_input, parent_app=parent_app, label_id=label_id, input_id=input_id)
                        children.append(form_group)
                    elif isinstance(v, dict):
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
                    else:
                        pass # list? optical channel?

            form = dbc.Form(children, style={'margin-top':'5px'})
            tab = dbc.Tab(form, label=tab_title)
            tabs.append(tab)

        self.children = dbc.Tabs(tabs)
        self.style={'margin-top': '5px'}
