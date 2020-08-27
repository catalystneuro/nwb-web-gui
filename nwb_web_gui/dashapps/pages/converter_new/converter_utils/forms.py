import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash_cool_components import FileExplorer


class FormItem(dbc.FormGroup):
    """Custom form group instance"""
    def __init__(self, label, form_input, key_name):
        super().__init__([])

        if key_name != 'path':
            self.children = dbc.Row([
                dbc.Col(label, width={'size':2}),
                dbc.Col(form_input, width={'size':10}, style={'justify-content': 'center', 'text-align': 'center'})
            ])
        else:
            explorer_btn = dbc.Button(id={'name': 'source_explorer', 'index': 0}, children=[html.I(className="far fa-folder")], style={'background-color': 'transparent', 'color': 'black', 'border': 'none'})
            self.children = dbc.Row([
                dbc.Col(label, width={'size':2}),
                dbc.Col(form_input, width={'size':8}, style={'justify-content': 'center', 'text-align': 'center'}),
                dbc.Col(explorer_btn, width={'size': 2})
            ])


class SourceForm(dbc.Card):
    def __init__(self, required, fields, parent_name):
        super().__init__([])

        self.required_fields = required

        all_inputs = []

        for k, v in fields.items():
            input_id = f'input_{parent_name}_{k}'
            label = dbc.Label(k)
            if k == 'type':
                options = [{'label': e, 'value': e} for e in v['enum']]
                form_input = dcc.Dropdown(
                    options=options,
                    id={'name': 'source_dropdown_input', 'id': input_id},
                    clearable=False,
                )
            elif v['type'] == 'string':
                form_input = dbc.Input(
                    placeholder=v['description'],
                    className='string_input',
                    type='input',
                    id={'name': 'source_string_input', 'id': input_id},
                )
            elif v['type'] == 'boolean':
                form_input = dbc.Checkbox(
                    className="form-check-input",
                    id={'name': 'source_boolean_input', 'id': input_id},
                )

            form_item = FormItem(label=label, form_input=form_input, key_name=k)
            all_inputs.append(form_item)

        form = dbc.Form(all_inputs)
        self.children = [
            dbc.CardHeader(parent_name.replace('_', ' ').title(), style={'text-align': 'center'}),
            dbc.CardBody(form)
        ]
