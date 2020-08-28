import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash_cool_components import FileExplorer, Keywords


class SourceFormItem(dbc.FormGroup):
    """Custom form group instance"""
    def __init__(self, label, form_input, key_name):
        super().__init__([])


        if key_name != 'path':
            self.children = dbc.Row([
                dbc.Col(label, width={'size':2}),
                dbc.Col(form_input, width={'size':10}, style={'justify-content': 'center', 'text-align': 'center'})
            ])
        else:
            explorer_btn = dbc.Button(id={'name': 'source_explorer', 'index': f'explorer_source_data_{key_name}'}, children=[html.I(className="far fa-folder")], style={'background-color': 'transparent', 'color': 'black', 'border': 'none'})
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
            if k == 'name':
                label_name = k
                label = dbc.Label(label_name)
            else:
                input_id = f'input_{parent_name}_{label_name}_{k}'
                if v['type'] == 'string' and k != 'type':
                    form_input = dbc.Input(
                        placeholder=v['description'],
                        id={'name': f'source_string_input', 'index': input_id},
                        className='string_input',
                        type='input'
                    )
                elif v['type'] == 'boolean' and k != 'type':
                    form_input = dbc.Checkbox(
                        id={'name': 'source_boolean_input', 'index': input_id}
                    )
                if k != 'type':
                    form_item = SourceFormItem(label=label, form_input=form_input, key_name=k)
                    all_inputs.append(form_item)

        form = dbc.Form(all_inputs)
        self.children = [
            dbc.CardHeader(parent_name.replace('_', ' ').title(), style={'text-align': 'center'}),
            dbc.CardBody(form)
        ]

class MetadataFormItem(dbc.FormGroup):
    def __init__(self, label, form_input):
        super().__init__([])

        self.children = [
            dbc.Row([
                dbc.Col(label, width={'size':2}),
                dbc.Col(form_input, width={'size':8})
            ])
        ]



class MetadataForms(dbc.Form):
    def __init__(self, fields, parent_name):
        super().__init__([])

        self.fields = fields
        self.parent_name = parent_name

        if self.fields['type'] == 'object':
            children = self.create_object_form()
        elif self.fields['type'] == 'array':
            children = self.create_array_form()

        self.children = children

    def create_object_form(self):
        children = []
        for k, v in self.fields['properties'].items():
            input_id = f'input_{self.parent_name}_{k}'
            label = dbc.Label(k)
            if v['type'] == 'string':
                if 'description' in v:
                    description = v['description']
                else:
                    description = ''
                form_input = dbc.Input(
                    id={'name': 'metadata_string_input', 'index': input_id},
                    placeholder=description
                )
                form_item = MetadataFormItem(label, form_input)
                children.append(form_item)
            elif v['type'] == 'array':
                pass
        
        return children

    def create_array_form(self):
        pass
