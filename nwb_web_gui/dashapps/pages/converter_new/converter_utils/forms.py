import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash_cool_components import FileExplorer, Keywords


class SourceFormItem(dbc.FormGroup):
    """Custom form group instance"""
    def __init__(self, label, form_input, add_explorer, explorer_id):
        super().__init__([])

        if add_explorer:
            explorer_btn = dbc.Button(id={'name': 'source_explorer', 'index': explorer_id}, children=[html.I(className="far fa-folder")], style={'background-color': 'transparent', 'color': 'black', 'border': 'none'})
            self.children = dbc.Row([
                dbc.Col(label, width={'size':2}),
                dbc.Col(form_input, width={'size':8}, style={'justify-content': 'center', 'text-align': 'center'}),
                dbc.Col(explorer_btn, width={'size': 2})
            ])
        else:
            self.children = dbc.Row([
                dbc.Col(label, width={'size':2}),
                dbc.Col(form_input, width={'size':10}, style={'justify-content': 'center', 'text-align': 'center'})
            ])


class SourceForm(dbc.Card):
    def __init__(self, required, fields, parent_name):
        super().__init__([])

        self.required_fields = required
        self.parent_name = parent_name

        parent = self.parent_name.replace(' ', '_')

        all_inputs = []
        for k, v in fields.items():
            label = dbc.Label(k)
            input_id = f'input_{parent}_{k}'
            if v['type'] == 'string':
                form_input = dbc.Input(
                    id={'name': 'source_string_input', 'index': input_id},
                    className='string_input',
                    type='input'
                )
            elif v['type'] == 'boolean':
                form_input = dbc.Checkbox(
                    id={'name': 'source_boolean_input', 'index': input_id}
                )
            if 'format' in v.keys():
                if v['format'] == 'file' or v['format'] == 'directory':
                    add_explorer = True
                    explorer_id = input_id.replace('input', 'explorer')
                else:
                    add_explorer = False
                    explorer_id = ''
            else:
                add_explorer = False
                explorer_id = ''

            form_item = SourceFormItem(label, form_input, add_explorer, explorer_id)
            all_inputs.append(form_item)

        form = dbc.Form(all_inputs)
        self.children = [
            dbc.CardHeader(self.parent_name.title(), style={'text-align': 'center'}),
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


class MetadataForms(dbc.Card):
    def __init__(self, fields, parent_name):
        super().__init__([])

        self.fields = fields
        self.parent_name = parent_name

        if self.fields['type'] == 'object':
            children = self.create_object_form()
        elif self.fields['type'] == 'array':
            self.fields = self.fields['items']
            children = self.create_object_form()

        self.children = [dbc.Container(dbc.Form(children), fluid=True)]
        self.style = {'padding-top': '1%'}

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
                    placeholder=description,
                    className='string_input',
                )
            elif v['type'] == 'array':
                form_input = Keywords(
                    id=input_id,
                    wrapperStyle={'box-shadow': 'none', 'border-radius': '2px', 'line-height': '5px'},
                    inputStyle={'line-height': '15px', 'height': '15px'}
                )
            form_item = MetadataFormItem(label, form_input)
            children.append(form_item)

        return children

    def create_array_form(self):
        pass
