import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
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
    def __init__(self, label, form_input, add_required=False):
        super().__init__([])

        if add_required:
            self.children = [
                dbc.Row([
                    dbc.Col([label, html.Span('*', style={'color': 'red'})], width={'size': 3}),
                    dbc.Col(form_input, width={'size': 8})
                ])
            ]
        else:
            self.children = [
                dbc.Row([
                    dbc.Col(label, width={'size': 3}),
                    dbc.Col(form_input, width={'size': 8})
                ])
            ]


class MetadataForm(dbc.Card):
    def __init__(self, schema, key, definitions=None, parent=None):
        super().__init__([])

        self.schema = schema
        self.parent = parent

        # Unique Card IDs are composed by parent id + key from json schema
        if parent is not None:
            self.id = parent.id + '_' + key
        else:
            self.id = key

        header_text = self.id.split('_')[-1]
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

            # If item is an object, e.g. NWBFile
            if 'type' in v and v['type'] == 'object':
                item = MetadataForm(schema=v, key=k, parent=self)

            # If item references an object on definitions, e.g. Device
            elif "$ref" in v:
                template_name = v["$ref"].split('/')[-1]
                schema = self.definitions[template_name]
                item = MetadataForm(schema=schema, key=k, parent=self)

            # If item is an array of subforms, e.g. ImagingPlane.optical_channels
            elif 'type' in v and (v['type'] == 'array'):
                if isinstance(v['items'], list):
                    form_input = html.Div([])
                    for i, iv in enumerate(v["items"]):
                        template_name = iv["$ref"].split('/')[-1]
                        schema = self.definitions[template_name]
                        iform = MetadataForm(schema=schema, key=k + f'_{i}', parent=self)
                        form_input.children.append(iform)
                    label = dbc.Label(k)
                    item = MetadataFormItem(label=label, form_input=form_input, add_required=required)
                elif isinstance(v['items'], dict):
                    input_id = f'input_{self.id}_{k}'
                    form_input = self.get_string_field_input(value=v, input_id=input_id)
                    label = dbc.Label(k)
                    item = MetadataFormItem(label, form_input, add_required=required)
            # If item is an input field, e.g. description
            elif 'type' in v and (v['type'] == 'string' or v['type'] == 'number'):
                input_id = f'input_{self.id}_{k}'
                form_input = self.get_string_field_input(value=v, input_id=input_id)
                label = dbc.Label(k)
                item = MetadataFormItem(label=label, form_input=form_input, add_required=required)

            else:
                continue

            self.body.children.append(item)

    @staticmethod
    def get_string_field_input(value, input_id):
        """
        Get component for user interaction. Types:
        - text
        - number
        - tag input
        - dropdown
        - datetime
        """
        if 'description' in value:
            description = value['description']
        else:
            description = ''

        if 'enum' in value:
            input_values = [{'label': e, 'value': e} for e in value['enum']]
            if 'default' in value:
                default = value['default']
            else:
                default = ''
            form_input_id = {'name': 'metadata_string_input', 'index': input_id}
            form_input = dcc.Dropdown(
                id=form_input_id,
                options=input_values,
                value=default,
                className='dropdown_input'
            )

        elif 'type' in value and value['type'] == 'array':
            form_input_id = {'name': 'metadata_keywords_input', 'index': input_id}
            form_input = TagInput(
                id=form_input_id,
                wrapperStyle={'box-shadow': 'none', 'border-radius': '2px', 'line-height': '5px'},
                inputStyle={'line-height': '15px', 'height': '15px'}
            )

        elif 'format' in value and value['format'] == 'date-time':
            form_input_id = {'name': 'metadata_date_input', 'index': input_id}
            form_input = DateTimePicker(
                id=form_input_id,
                style={"border": "solid 1px", "border-color": "#ced4da", "border-radius": "5px", "color": '#545057'}
            )

        elif 'format' in value and value['format'] == 'long':
            form_input_id = {'name': 'metadata_string_input', 'index': input_id}
            form_input = dbc.Textarea(
                id=form_input_id,
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
            form_input_id = {'name': 'metadata_string_input', 'index': input_id}
            form_input = dbc.Input(
                id=form_input_id,
                className='string_input',
                type=input_type,
                step=step
            )

        input_and_tooltip = html.Div([
            html.Div(
                form_input,
                id=form_input_id['index'] + '_' + form_input_id['name']
            ),
            dbc.Tooltip(
                description,
                target=form_input_id['index'] + '_' + form_input_id['name']
            ),
        ])

        return input_and_tooltip
