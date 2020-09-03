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
            if k in self.required_fields:
                add_required = True
            else:
                add_required = False
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
    def __init__(self, label, form_input, sublist=False, add_required=False):
        super().__init__([])

        if not sublist:
            if add_required:
                self.children = [
                    dbc.Row([
                        dbc.Col([label, html.Span('*', style={'color': 'red'})], width={'size': 2}),
                        dbc.Col(form_input, width={'size': 8})
                    ])
                ]
            else:
                self.children = [
                    dbc.Row([
                        dbc.Col(label, width={'size': 2}),
                        dbc.Col(form_input, width={'size': 8})
                    ])
                ]
        else:
            if add_required:
                self.children = [
                    dbc.Row([
                        dbc.Col([label, html.Span('*', style={'color': 'red'})], width={'size': 4}),
                        dbc.Col(form_input, width={'size': 8})
                    ])
                ]
            else:
                self.children = [
                    dbc.Row([
                        dbc.Col(label, width={'size': 4}),
                        dbc.Col(form_input, width={'size': 8})
                    ])
                ]



class MetadataForm(dbc.Card):
    def __init__(self, schema, definitions=None, parent=None):
        super().__init__([])

        if definitions is None:
            self.definitions = schema['definitions']

        self.make_form(properties=schema['properties'])

        self.


    def make_form(self, properties):
        """Isso aqui faz isso"""

        if type[''] == object:
            itemform = MetadataForm(schema=behavior, parent=self)

        if type == string:
            itemform =

    def

    def



class MetadataForms(dbc.Card):
    def __init__(self, fields, key_name, form_style, definitions=None, composite_children=None):
        super().__init__([])

        self.fields = fields
        self.key_name = key_name
        self.required_fields = []

        if definitions is not None:
            self.definitions = definitions

        if form_style == 'composite':
            self.composite_children = composite_children

            children = self.iter_composite_form(self.fields['properties'], forms=[])
            self.children = [
                dbc.CardHeader(key_name),
                dbc.CardBody([f for f in children])
            ]
        else:
            self.required_fields = self.fields['required']

            if self.fields['type'] == 'object':
                children = self.create_object_form(self.fields)
            elif self.fields['type'] == 'array':
                children = self.create_object_form(self.fields['items'])

            self.children = [
                dbc.CardHeader(key_name),
                dbc.CardBody(children)
            ]

        self.style = {'margin-top': '1%'}

    def iter_composite_form(self, fields, forms=[]):

        for k, v in fields.items():
            if k in self.composite_children:
                if 'type' in v and v['type'] == 'object':
                    if 'required' in v:
                        self.required_fields = v['required']
                    else:
                        self.required_fields = []
                    children = self.create_object_form(v, composite_key=k)
                    element = dbc.Form(dbc.Row([
                        dbc.Col(html.H4(k), width={'size': 12}),
                        dbc.Col(children, width={'size': 12})
                    ], style={'margin': '3px'}))
                elif 'type' in v and v['type'] == 'array':
                    if 'required' in v['items']:
                        self.required_fields = v['items']['required']
                    children = self.create_object_form(v['items'], composite_key=k)
                    element = dbc.Form(dbc.Row([
                        dbc.Col(html.H4(k, className="card-title"), width={'size': 12}),
                        dbc.Col(children, width={'size': 12})
                    ], style={'margin': '3px'}))
                elif 'type' not in v and '$ref' in v:
                    ref_key = v['$ref'].split('/')[-1]
                    extra_key = f'{k}_{ref_key}'
                    def_form = self.get_definitions_items(ref_key, extra_key)
                    element = dbc.Row([
                        dbc.Col(html.H4(ref_key), className="card-title", width={'size': 12}),
                        dbc.Col(def_form, width={'size': 12})
                    ], style={'margin': '3px'})
                forms.append(element)
            else:
                if isinstance(v, dict):
                    self.iter_composite_form(v, forms=forms)

        return forms

    def create_object_form(self, fields, composite_key=None, sublist=False):
        children = []
        subform_layout = None

        for k, v in fields['properties'].items():
            if composite_key is None:
                input_id = f'input_{self.key_name}_{k}'
            else:
                input_id = f'input_{self.key_name}_{composite_key}_{k}'

            label = dbc.Label(k)
            if k in self.required_fields:
                add_required = True
            else:
                add_required = False
            if v['type'] == 'string' or v['type'] == 'number':
                form_input = self.get_string_field_input(v, input_id)
            elif v['type'] == 'array':
                if 'format' in v and v['format'] == 'keywords':
                    form_input = TagInput(
                        id=input_id,
                        wrapperStyle={'box-shadow': 'none', 'border-radius': '2px', 'line-height': '5px'},
                        inputStyle={'line-height': '15px', 'height': '15px'}
                    )
                else:
                    if 'properties' in v['items']:
                        sublist_children = []
                        if 'required' in v['items']:
                            self.required_fields = v['items']['required']
                        else:
                            self.required_fields = []
                        for lbl, value in v['items']['properties'].items():
                            if lbl in self.required_fields:
                                add_required = True
                            else:
                                add_required = False
                            input_id_aux = f'{input_id}_{lbl}'
                            label = dbc.Label(lbl)
                            form_input = self.get_string_field_input(value, input_id_aux)
                            form_item = MetadataFormItem(label, form_input, sublist=True, add_required=add_required)
                            sublist_children.append(form_item)

                        sublist_form = dbc.Card(dbc.CardBody(dbc.Form(sublist_children)))
                        subform_layout = dbc.Row([
                            dbc.Col(
                                dbc.Label(k), width={'size': 2}
                            ),
                            dbc.Col(
                                sublist_form, width={'size': 8}
                            )
                        ])
                    if 'allOf' in v['items']:
                        for item in v['items']['allOf']:
                            if isinstance(item, dict):
                                if '$ref' in item.keys():
                                    ref_key = item['$ref'].split('/')[-1]
                                    extra_key = f'{composite_key}_{ref_key}'
                                    definition_form = dbc.Card(dbc.CardBody(self.get_definitions_items(ref_key, extra_key, sublist=True)), style={'margin-top': '1%'})
                                    definitions_layout = dbc.Row([
                                        dbc.Col(
                                            dbc.Label(ref_key), width={'size': 2}
                                        ),
                                        dbc.Col(definition_form, width={'size': 8})
                                    ])
                                    if subform_layout is not None:
                                        subform_layout.children.append(dbc.Col(definitions_layout, width={'size': 12}))
                                    else:
                                        subform_layout = definitions_layout

            if subform_layout is None:
                form_item = MetadataFormItem(label, form_input, sublist, add_required)
                children.append(form_item)
            else:
                children.append(subform_layout)

        return children

    def get_definitions_items(self, ref_key, extra_key, sublist=False):
        ref = self.definitions[ref_key]

        if ref['type'] == 'object':
            if 'required' in ref:
                self.required_fields = ref['required']
            form = dbc.Form(self.create_object_form(ref, composite_key=extra_key, sublist=sublist))
        elif ref['type'] == 'array':
            if 'required' in ref['items']:
                self.required_fields = ref['items']['required']
            form = dbc.Form(self.create_object_form(ref['items'], sublist=sublist))

        if 'allOf' in ref:
            subforms = [form]
            for item in ref['allOf']:
                if '$ref' in item:
                    ref_key = item['$ref'].split('/')[-1]
                    key = f'{extra_key}_{ref_key}'
                    subform = self.get_definitions_items(ref_key, key, sublist=True)
                    subform_layout = dbc.Row([
                        # dbc.Col(dbc.Label(ref_key), width={'size': 12}),
                        dbc.Col(subform, width={'size': 12})
                    ])
                    subforms.append(subform_layout)

            output_form = dbc.Container(subforms)
            return output_form

        return form

    def get_string_field_input(self, value, input_id):

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
            form_input = dcc.Dropdown(
                id={'name': 'metadata_string_input', 'index': input_id},
                options=input_values,
                value=default,
                className='dropdown_input'
            )
        else:
            if 'format' in value and value['format'] == 'date-time':
                form_input = DateTimePicker(
                    id={'name': 'metadata_date_input', 'index': input_id},
                    style={"border": "solid 1px", "border-color": "#ced4da", "border-radius": "5px", "color": '#545057'}
                )
            elif 'format' in value and value['format'] == 'long':
                form_input = dbc.Textarea(
                    id={'name': 'metadata_string_input', 'index': input_id},
                    placeholder=description,
                    className='string_input',
                    bs_size="lg",
                    style={'font-size': '16px'}
                )
            else:
                input_type = value['type']
                if input_type == 'number':
                    step = 0.01
                else:
                    step = ''
                form_input = dbc.Input(
                    id={'name': 'metadata_string_input', 'index': input_id},
                    placeholder=description,
                    className='string_input',
                    type=input_type,
                    step=step
                )

        return form_input
