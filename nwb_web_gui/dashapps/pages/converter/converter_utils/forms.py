import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import warnings
from dash_cool_components import KeyedFileBrowser, TagInput, DateTimePicker


class SourceFormItem(dbc.FormGroup):
    """Custom form group instance"""
    def __init__(self, label, form_input, add_explorer, explorer_id, add_required):
        super().__init__([])

        if add_explorer:
            explorer_btn = dbc.Button(id={'name': 'source_explorer', 'index': explorer_id}, children=[html.I(className="far fa-folder")], style={'background-color': 'transparent', 'color': 'black', 'border': 'none'})
            if add_required:
                self.children = dbc.Row([
                    dbc.Col([label, html.Span('*', style={'color': 'red'})], width={'size': 2}),
                    dbc.Col(form_input, width={'size': 8}, style={'justify-content': 'center', 'text-align': 'center'}),
                    dbc.Col(explorer_btn, width={'size': 2}, style={'text-align': 'left'})
                ])
            else:
                self.children = dbc.Row([
                    dbc.Col(label, width={'size': 2}),
                    dbc.Col(form_input, width={'size': 8}, style={'justify-content': 'center', 'text-align': 'center'}),
                    dbc.Col(explorer_btn, width={'size': 2}, style={'text-align': 'left'})
                ])
        else:
            if add_required:
                self.children = dbc.Row([
                    dbc.Col([label, html.Span('*', style={'color': 'red'})], width={'size': 2}),
                    dbc.Col(form_input, width={'size': 10}, style={'justify-content': 'left', 'text-align': 'left'})
                ])
            else:
                self.children = dbc.Row([
                    dbc.Col(label, width={'size': 2}),
                    dbc.Col(form_input, width={'size': 10}, style={'justify-content': 'left', 'text-align': 'left'})
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
            explorer_id = input_id.replace('input', 'explorer')
            add_required = k in self.required_fields

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

            form_item = SourceFormItem(label, form_input, add_explorer, explorer_id, add_required)
            all_inputs.append(form_item)

        form = dbc.Form(all_inputs)
        self.children = [
            dbc.CardHeader(self.parent_name.title(), style={'text-align': 'left'}),
            dbc.CardBody(form)
        ]

        self.style = {'margin-top': '1%'}


class MetadataFormItem(dbc.FormGroup):
    def __init__(self, label, value, input_id, parent, add_required=False):
        super().__init__([])

        self.parent = parent

        field_input = self.get_field_input(value=value, input_id=input_id)

        if add_required:
            self.children = [
                dbc.Row([
                    dbc.Col([label, html.Span('*', style={'color': 'red'})], width={'size': 3}),
                    dbc.Col(field_input, width={'size': 8})
                ])
            ]
        else:
            self.children = [
                dbc.Row([
                    dbc.Col(label, width={'size': 3}),
                    dbc.Col(field_input, width={'size': 8})
                ])
            ]

    def get_field_input(self, value, input_id, description=None):
        """
        Get component for user interaction. Types:
        - string
        - number
        - tag input
        - datetime
        - string choice
        - link choice
        - list
        """

        if isinstance(value, list):
            field_input_id = {'name': 'metadata-list-input', 'index': input_id}
            field_input = html.Div(value, id=field_input_id)
            description = ''

        elif 'enum' in value:
            input_values = [{'label': e, 'value': e} for e in value['enum']]
            if 'default' in value:
                default = value['default']
            else:
                default = ''
            field_input_id = {'name': 'metadata-string-input', 'index': input_id}
            field_input = dcc.Dropdown(
                id=field_input_id,
                options=input_values,
                value=default,
                className='dropdown_input'
            )

        elif 'type' in value and value['type'] == 'array':
            field_input_id = {'name': 'metadata-tags-input', 'index': input_id}
            field_input = TagInput(
                id=field_input_id,
                wrapperStyle={'box-shadow': 'none', 'border-radius': '2px', 'line-height': '5px'},
                inputStyle={'line-height': '15px', 'height': '15px'}
            )

        elif 'format' in value and value['format'] == 'date-time':
            field_input_id = {'name': 'metadata-date-input', 'index': input_id}
            field_input = DateTimePicker(
                id=field_input_id,
                style={"border": "solid 1px", "border-color": "#ced4da", "border-radius": "5px", "color": '#545057'}
            )

        elif 'format' in value and value['format'] == 'long':
            field_input_id = {'name': 'metadata-string-input', 'index': input_id}
            field_input = dbc.Textarea(
                id=field_input_id,
                className='string_input',
                bs_size="lg",
                style={'font-size': '16px'}
            )
        else:
            input_type = value['type']
            if input_type == 'number':
                step = 1
            else:
                step = ''
            field_input_id = {'name': 'metadata-string-input', 'index': input_id}
            field_input = dbc.Input(
                id=field_input_id,
                className='string_input',
                type=input_type,
                step=step
            )

        # Add tooltip to input field
        if description is None:
            description = value.get('description', '')

        input_and_tooltip = html.Div([
            html.Div(
                field_input,
                id='wrapper-' + field_input_id['index'] + '-' + field_input_id['name']
            ),
            dbc.Tooltip(
                description,
                target='wrapper-' + field_input_id['index'] + '-' + field_input_id['name']
            ),
        ])

        return input_and_tooltip


class MetadataForm(dbc.Card):
    def __init__(self, schema, key, definitions=None, parent=None):
        super().__init__([])

        self.schema = schema
        self.parent = parent

        # Unique Card IDs are composed by parent id + key from json schema
        if parent is not None:
            self.id = parent.id + '-' + key
        else:
            self.id = key

        header_text = self.id.split('-')[-1]
        self.header = dbc.CardHeader([html.H4(header_text, className="title_" + key)])
        self.body = dbc.CardBody([])
        self.children = [self.header, self.body]

        if definitions is None and parent is None:
            self.definitions = schema['definitions']
        else:
            self.definitions = parent.definitions

        self.required_fields = schema.get('required', '')

        if 'properties' in schema:
            self.make_form(properties=schema['properties'])

    def make_form(self, properties):
        """Iterates over properties of schema and assembles form items"""
        for k, v in properties.items():
            required = k in self.required_fields

            # If item is a pynwb object or reference to an object on definitions,
            # e.g. NWBFile, make subform
            if 'type' in v and v['type'] == 'object':
                item = MetadataForm(schema=v, key=k, parent=self)
                self.body.children.append(item)
                continue
            elif "$ref" in v:
                template_name = v["$ref"].split('/')[-1]
                schema = self.definitions[template_name]
                item = MetadataForm(schema=schema, key=k, parent=self)
                self.body.children.append(item)
                continue

            # If item is a pynwb field
            if 'type' in v and (v['type'] == 'array'):
                # If field is an array of subforms, e.g. ImagingPlane.optical_channels
                if isinstance(v['items'], list):
                    value = []
                    for i, iv in enumerate(v["items"]):
                        template_name = iv["$ref"].split('/')[-1]
                        schema = self.definitions[template_name]
                        iform = MetadataForm(schema=schema, key=k + f'-{i}', parent=self)
                        value.append(iform)
                # If field is an array of strings, e.g. NWBFile.experimenter
                elif isinstance(v['items'], dict):
                    value = v
            # If field is a simple input field, e.g. description
            elif 'type' in v and (v['type'] == 'string' or v['type'] == 'number'):
                value = v
            # If field is something not yet implemented
            else:
                warnings.warn(f'Field input not yet implemented for {k}')
                continue

            label = dbc.Label(k)
            input_id = f'{self.id}-{k}'
            item = MetadataFormItem(
                label=label,
                value=value,
                input_id=input_id,
                parent=self,
                add_required=required
            )
            self.body.children.append(item)
