import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash_cool_components import TagInput, DateTimePicker
from nwb_web_gui.dashapps.utils.make_components import make_filebrowser_modal
import numpy as np
from pathlib import Path
import warnings
import json


class SchemaFormItem(dbc.FormGroup):
    def __init__(self, label, value, input_id, parent, required=False):
        super().__init__([])

        self.parent = parent

        field_input = self.get_field_input(value=value, input_id=input_id, required=required)

        if required:
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

    def get_field_input(self, value, input_id, description=None, required=False):
        """
        Get component for user interaction. Types:
        - string
        - number
        - tag list
        - datetime
        - string choice
        - link choice
        - list of subforms
        - boolean
        - path to file or dir
        """

        owner_class = self.parent.owner_class
        compound_id = {
            'type': 'metadata-input',
            'index': input_id,
            'data_type': '',
            'container_id': self.parent.container.id
        }

        default = None

        if isinstance(value, list):
            compound_id['data_type'] = 'list'
            field_input = html.Div(value)  # id=compound_id)
            description = ''

        elif 'enum' in value:
            input_values = [{'label': e, 'value': e} for e in value['enum']]
            default = value.get('default', '')
            compound_id['data_type'] = 'choicestring'
            field_input = dcc.Dropdown(
                id=compound_id,
                options=input_values,
                value=default,
                className='dropdown_input'
            )

        elif 'target' in value:
            compound_id['data_type'] = 'link'
            field_input = dcc.Dropdown(
                id=compound_id,
                options=[],
                value='',
                className='dropdown_input',
                searchable=False,
                clearable=False
            )

        elif 'type' in value and value['type'] == 'array':
            compound_id['data_type'] = 'tags'
            field_input = TagInput(
                id=compound_id,
                wrapperStyle={'box-shadow': 'none', 'border-radius': '2px', 'line-height': '5px'},
                inputStyle={'line-height': '15px', 'height': '15px'}
            )

        elif 'format' in value and value['format'] == 'date-time':
            compound_id['data_type'] = 'datetime'
            field_input = DateTimePicker(
                id=compound_id,
            )

        elif 'format' in value and value['format'] == 'long':
            compound_id['data_type'] = 'string'
            field_input = dbc.Textarea(
                id=compound_id,
                className='string_input',
                bs_size="lg",
                style={'font-size': '16px'}
            )

        elif 'format' in value and value['format'] in ['file', 'directory']:
            compound_id['data_type'] = 'path'
            input_path = dbc.Input(
                id=compound_id,
                className='string_input',
                type='input'
            )
            btn_id = "open-filebrowser-" + compound_id['index']
            btn_open_filebrowser = dbc.Button(
                id=btn_id,
                children=[html.I(className="far fa-folder")],
                style={'background-color': 'transparent', 'color': 'black', 'border': 'none'}
            )
            modal_id = "modal-filebrowser-" + compound_id['index']
            modal = make_filebrowser_modal(
                parent_app=self.parent.container.parent_app,
                modal_id=modal_id,
                display=value['format']
            )
            # Create internal trigger component and add it to parent Container
            trigger_id = {'type': 'internal-trigger-update-forms-values', 'parent': self.parent.container.id, 'index': compound_id['index']}
            trigger = html.Div(id=trigger_id, style={'display': 'none'})
            self.parent.container.children_triggers.append(trigger)

            self.register_filebrowser_callbacks(
                modal_id=modal_id,
                button_id=btn_id,
                trigger_id=trigger_id
            )

            field_input = html.Div([
                dbc.InputGroup([
                    input_path,
                    dbc.InputGroupAddon(btn_open_filebrowser, addon_type="append"),
                ]),
                modal
            ])

        elif value['type'] == 'boolean':
            compound_id['data_type'] = 'boolean'
            default = value['default']
            field_input = dbc.Checkbox(
                id=compound_id,
                checked=value['default']
            )

        else:
            input_type = value['type']
            if input_type == 'number':
                step = 1
                compound_id['data_type'] = 'number'
            elif 'name' in input_id:
                step = ''
                compound_id['data_type'] = 'name'
            else:
                step = ''
                compound_id['data_type'] = 'string'
            field_input = dbc.Input(
                id=compound_id,
                className='string_input',
                type=input_type,
                step=step
            )

        # Add data
        if not isinstance(value, list):
            if default is None:
                self.parent.container.data.update({
                    input_id: {
                        'compound_id': compound_id,
                        'owner_class': str(owner_class),
                        'target': value.get('target', None),
                        'value': None,
                        'required': required
                    }
                })
            else:
                self.parent.container.data.update({
                    input_id: {
                        'compound_id': compound_id,
                        'owner_class': str(owner_class),
                        'target': value.get('target', None),
                        'value': default,
                        'required': required
                    }
                })

        # Add tooltip to input field
        if description is None:
            description = value.get('description', '')

        input_and_tooltip = html.Div([
            html.Div(
                field_input,
                id='wrapper-' + compound_id['index'] + '-' + compound_id['type']
            ),
            dbc.Tooltip(
                description,
                target='wrapper-' + compound_id['index'] + '-' + compound_id['type']
            ),
        ])

        return input_and_tooltip

    def register_filebrowser_callbacks(self, modal_id, button_id, trigger_id):
        """Register callbacks for filebroswer component"""
        # trigger_id = {type: internal-trigger-update-form-values, index: index_class}

        @self.parent.container.parent_app.callback(
            Output(modal_id, 'is_open'),
            [
                Input(button_id, 'n_clicks'),
                Input(modal_id + "-close", 'n_clicks')
            ],
            [State(modal_id, 'is_open')]
        )
        def toggle_filebrowser(click_open, click_close, is_open):
            """Toggle modal open/close"""
            if click_open or click_close:
                return not is_open
            else:
                return is_open

        @self.parent.container.parent_app.callback(
            [Output(trigger_id, 'children'), Output(f'{modal_id}-close', 'n_clicks')],
            [Input('submit-filebrowser-' + modal_id, 'n_clicks')],
            [State('chosen-filebrowser-' + modal_id, 'value')]
        )
        def get_path_values(click, chosen_path):
            """
            Get path value from file browser, update Container data and trigger
            frontend components updates
            """
            if click:
                # Update Container internal dictionary value
                self.parent.container.data[trigger_id['index']]['value'] = chosen_path
                # Triggers components update
                return str(np.random.rand()), 1
            return '', None


class SchemaForm(dbc.Card):
    """
    Form generated by JSON Schema.
    """
    def __init__(self, schema, key, container=None, parent_form=None):
        super().__init__([])

        self.schema = schema
        self.owner_class = schema.get('tag', '')
        self.parent_form = parent_form

        # Unique Card IDs are composed by parent id + key from json schema
        if parent_form is None:
            self.id = key
            self.container = container
        else:
            self.id = parent_form.id + '-' + key
            self.container = parent_form.container

        if 'definitions' in self.container.schema:
            self.definitions = self.container.schema['definitions']
        else:
            self.definitions = dict()

        header_text = schema.get('title', self.id.split('-')[-1])
        self.header = dbc.CardHeader(
            [html.H4(header_text, className="title_" + key)],
            style={'padding': '10px'}
        )
        self.body = dbc.CardBody([])
        self.children = [self.header, self.body]

        self.required_fields = schema.get('required', '')

        self.style = {'padding': '0px', 'margin-top': '10px'}

        # Construct form
        if 'properties' in schema:
            self.make_form(properties=schema['properties'])

    def make_form(self, properties):
        """Iterates over properties of schema and assembles form items"""
        for k, v in properties.items():
            required = k in self.required_fields

            # If item is an object or reference to an object on definitions, make subform
            if 'type' in v and v['type'] == 'object':
                item = SchemaForm(schema=v, key=k, parent_form=self)
                self.body.children.append(item)
                continue
            elif "$ref" in v:
                template_name = v["$ref"].split('/')[-1]
                schema = self.definitions[template_name]
                item = SchemaForm(schema=schema, key=k, parent_form=self)
                self.body.children.append(item)
                continue

            # If item is a field
            if 'type' in v and (v['type'] == 'array'):
                # If field is an array of subforms, e.g. ImagingPlane.optical_channels
                if isinstance(v['items'], list):
                    value = []
                    template_name = v['items'][0]['$ref'].split('/')[-1]
                    schema = self.definitions[template_name]
                    for index in range(v['minItems']):
                        iform = SchemaForm(schema=schema, key=f'{k}-{index}', parent_form=self)
                        value.append(iform)

                # If field is an array of strings, e.g. NWBFile.experimenter
                elif isinstance(v['items'], dict):
                    value = v
            # If field is a simple input field, e.g. description
            elif 'type' in v and v['type'] in ['string', 'number', 'boolean']:
                value = v
            # If field is something not yet implemented
            else:
                warnings.warn(f'Field input not yet implemented for {k}')
                continue

            label = dbc.Label(k)
            input_id = f'{self.id}-{k}'
            item = SchemaFormItem(
                label=label,
                value=value,
                input_id=input_id,
                parent=self,
                required=required
            )
            self.body.children.append(item)


class SchemaFormContainer(html.Div):
    """
    Root Container for Schema Forms

    IDs exposed for external trigger of update functions:
    id + '-external-trigger-update-forms-values'
    id + '-external-trigger-update-links-values'
    """
    def __init__(self, id, schema, parent_app):
        super().__init__([])

        self.id = id
        self.schema = schema
        self.parent_app = parent_app
        self.data = {}
        self.children_forms = []

        # Hidden componentes that serve to trigger callbacks
        self.children_triggers = [
            html.Div(id={'type': 'external-trigger-update-forms-values', 'index': id + '-external-trigger-update-forms-values'}, style={'display': 'none'}),
            html.Div(id={'type': 'external-trigger-update-links-values', 'index': f'{id}-external-trigger-update-links-values'}, style={"display": "none"}),
            html.Div(id=f'{id}-external-trigger-update-internal-dict', style={'display': 'none'}),
            html.Div(id=f'{id}-output-update-finished-verification', style={'display': 'none'}),
            html.Div(id=id + '-trigger-update-links-values', style={'display': 'none'}),
            html.Div(id=id + '-output-placeholder-links-values', style={'display': 'none'})
        ]

        if schema:
            self.construct_children_forms()
        else:
            self.children = self.children_triggers

        self.update_forms_links_callback_outputs = [
            Output({'type': 'metadata-input', 'container_id': f"{self.id}", 'data_type': 'link', 'index': ALL}, 'options'),
            Output({'type': 'metadata-input', 'container_id': f"{self.id}", 'data_type': 'link', 'index': ALL}, 'value'),
            Output(self.id + '-output-placeholder-links-values', 'children')
        ]

        self.update_forms_values_callback_outputs = [
            Output({'type': 'metadata-input', 'container_id': f"{self.id}", 'data_type': 'path', 'index': ALL}, 'value'),
            Output({'type': 'metadata-input', 'container_id': f"{self.id}", 'data_type': 'boolean', 'index': ALL}, 'checked'),
            Output({'type': 'metadata-input', 'container_id': f"{self.id}", 'data_type': 'string', 'index': ALL}, 'value'),
            Output({'type': 'metadata-input', 'container_id': f"{self.id}", 'data_type': 'datetime', 'index': ALL}, 'defaultValue'),
            Output({'type': 'metadata-input', 'container_id': f"{self.id}", 'data_type': 'tags', 'index': ALL}, 'injectedTags'),
            Output({'type': 'metadata-input', 'container_id': f"{self.id}", 'data_type': 'name', 'index': ALL}, 'value'),
            Output({'type': 'metadata-input', 'container_id': f"{self.id}", 'data_type': 'number', 'index': ALL}, 'value'),
            Output(f'{self.id}-trigger-update-links-values', 'children')
        ]
        self.update_forms_values_callback_states = [
            State({'type': 'metadata-input', 'container_id': f"{self.id}", 'data_type': 'path', 'index': ALL}, 'value'),
            State({'type': 'metadata-input', 'container_id': f"{self.id}", 'data_type': 'boolean', 'index': ALL}, 'checked'),
            State({'type': 'metadata-input', 'container_id': f"{self.id}", 'data_type': 'string', 'index': ALL}, 'value'),
            State({'type': 'metadata-input', 'container_id': f"{self.id}", 'data_type': 'datetime', 'index': ALL}, 'value'),
            State({'type': 'metadata-input', 'container_id': f"{self.id}", 'data_type': 'tags', 'index': ALL}, 'value'),
            State({'type': 'metadata-input', 'container_id': f"{self.id}", 'data_type': 'name', 'index': ALL}, 'value'),
            State({'type': 'metadata-input', 'container_id': f"{self.id}", 'data_type': 'number', 'index': ALL}, 'value'),
        ]

        @self.parent_app.callback(
            Output(f'{self.id}-output-update-finished-verification', 'children'),
            [Input(f'{self.id}-external-trigger-update-internal-dict', 'children')],
            [
                State({'type': 'metadata-input', 'container_id': self.id, 'data_type': 'path', 'index': ALL}, 'value'),
                State({'type': 'metadata-input', 'container_id': self.id, 'data_type': 'boolean', 'index': ALL}, 'checked'),
                State({'type': 'metadata-input', 'container_id': self.id, 'data_type': 'string', 'index': ALL}, 'value'),
                State({'type': 'metadata-input', 'container_id': self.id, 'data_type': 'datetime', 'index': ALL}, 'value'),
                State({'type': 'metadata-input', 'container_id': self.id, 'data_type': 'tags', 'index': ALL}, 'value'),
                State({'type': 'metadata-input', 'container_id': self.id, 'data_type': 'link', 'index': ALL}, 'value'),
                State({'type': 'metadata-input', 'container_id': self.id, 'data_type': 'name', 'index': ALL}, 'value'),
                State({'type': 'metadata-input', 'container_id': self.id, 'data_type': 'number', 'index': ALL}, 'value'),
                State({'type': 'metadata-input', 'container_id': self.id, 'data_type': ALL, 'index': ALL}, 'id'),
            ]
        )
        def update_internal_dict(trigger, path_values, boolean_values,
                                 string_values, datetime_values, tags_values,
                                 link_values, name_values, number_values, ids):

            if trigger is None:
                return []

            boolean_counter = 0
            path_counter = 0
            datetime_counter = 0
            string_counter = 0
            tags_counter = 0
            link_counter = 0
            names_counter = 0
            number_counter = 0

            for e in ids:
                for k, v in self.data.items():
                    if e['index'] == k:
                        if e['data_type'] == 'path':
                            root_path = Path(self.parent_app.server.config['DATA_PATH']).parent
                            path_v = path_values[path_counter] if path_values[path_counter] is not None else ''
                            field_value = str(root_path / path_v)
                            path_counter += 1
                        elif e['data_type'] == 'boolean':
                            field_value = boolean_values[boolean_counter]
                            boolean_counter += 1
                        elif e['data_type'] == 'datetime':
                            field_value = datetime_values[datetime_counter]
                            datetime_counter += 1
                        elif e['data_type'] == 'string':
                            field_value = string_values[string_counter]
                            string_counter += 1
                        elif e['data_type'] == 'name':
                            field_value = name_values[names_counter]
                            names_counter += 1
                        elif e['data_type'] == 'number':
                            field_value = number_values[number_counter]
                            number_counter += 1
                        elif e['data_type'] == 'tags':
                            field_value = tags_values[tags_counter]
                            tags_counter += 1
                        elif e['data_type'] == 'link':
                            field_value = link_values[link_counter]
                            link_counter += 1

                        self.data[k]['value'] = field_value

            return str(np.random.rand())

        @self.parent_app.callback(
            self.update_forms_values_callback_outputs,
            [
                Input({'type': 'external-trigger-update-forms-values', 'index': ALL}, 'children'),
                Input({'type': 'internal-trigger-update-forms-values', 'parent': self.id, 'index': ALL}, 'children')
            ],
            self.update_forms_values_callback_states

        )
        def update_forms_values(trigger, trigger_all, *states):
            ctx = dash.callback_context
            trigger_source = ctx.triggered[0]['prop_id'].split('.')[0]
            context = json.loads(trigger_source)

            if context['type'] == 'external-trigger-update-forms-values' and all((trg is None) or trg == [] for trg in trigger):
                raise dash.exceptions.PreventUpdate

            if context['type'] == 'internal-trigger-update-forms-values' and all((trg is None) or trg == [] or trg == '' for trg in trigger_all):
                raise dash.exceptions.PreventUpdate

            output_path = []
            output_bool = []
            output_string = []
            output_date = []
            output_tags = []
            output_link = []
            output_name = []
            output_number = []

            curr_data = list()
            for v in self.data.values():
                if v['compound_id']['data_type'] == 'path':
                    output_path.append(v['value'])
                elif v['compound_id']['data_type'] == 'boolean':
                    output_bool.append(v['value'])
                elif v['compound_id']['data_type'] == 'string':
                    output_string.append(v['value'])
                elif v['compound_id']['data_type'] == 'datetime':
                    output_date.append(v['value'])
                elif v['compound_id']['data_type'] == 'tags':
                    tags_values = v['value'] if v['value'] is not None else []
                    output_tags.append([{"index": i, "displayValue": e} for i, e in enumerate(tags_values)])
                elif v['compound_id']['data_type'] == 'link':
                    pass
                elif v['compound_id']['data_type'] == 'name':
                    output_name.append(v['value'])
                elif v['compound_id']['data_type'] == 'number':
                    output_number.append(v['value'])

            output = [
                output_path, output_bool, output_string, output_date, output_tags,
                output_name, output_number, 1
            ]

            return output

        @self.parent_app.callback(
            self.update_forms_links_callback_outputs,
            [
                Input(self.id + '-trigger-update-links-values', 'children'),
                Input({'type': 'external-trigger-update-links-values', 'index': ALL}, 'children')
            ],
            [State({'type': 'metadata-input', 'container_id': f"{self.id}", 'data_type': 'name', 'index': ALL}, 'value')]
        )
        def update_forms_links(trigger, trigger_all, name_change):
            ctx = dash.callback_context
            trigger_source = ctx.triggered[0]['prop_id'].split('.')[0]

            if 'index' in trigger_source:
                trigger_source = json.loads(trigger_source)['index']

            i = 0
            for k, v in self.data.items():
                if v['compound_id']['data_type'] == 'name':
                    self.data[k]['value'] = name_change[i]
                    i += 1

            # Get specific options for each link dropdown
            list_options = []
            list_values = []
            for k, v in self.data.items():
                if v['target'] is not None:
                    target_class = v['target']
                    options = [
                        {'label': v['value'], 'value': v['value']}
                        for v in self.data.values() if
                        (v['owner_class'] == target_class and 'name' in v['compound_id']['index'])
                    ]
                    list_values.append(options[0]['value'])
                    list_options.append(options)

            for sublist in list_options[:]:
                for e in sublist[:]:
                    if e['value'] is None:
                        sublist.remove(e)

            output = [list_options, list_values, [1]]

            return output

    def update_data(self, data, key=None):
        """Update data in the internal mapping dictionary of this Container"""
        if key is None:
            key = ''

        # Update dict with incoming data
        for k, v in data.items():
            # If value is a dictionary
            if isinstance(v, dict):
                if key != '':
                    inner_key = f'{key}-{k}'
                else:
                    inner_key = k
                self.update_data(data=v, key=inner_key)
            # If value is a string, number, list or boolean
            else:
                component_id = key + '-' + k   # e.g. NWBFile-session_description
                self.data[component_id]['value'] = v

    def construct_children_forms(self):
        # Construct children forms
        if 'properties' in self.schema:
            for form_key, form_value in self.schema['properties'].items():
                iform = SchemaForm(
                    schema=form_value,
                    key=form_key,
                    container=self
                )
                self.children_forms.append(iform)
        self.children = self.children_forms + self.children_triggers

    def data_to_nested(self):
        """
        Read internal class dict (containing ids, values, etc) and convert to nested
        dict (data format)

        Returns:
            alert_children [list | None]: Alerts children if required fields empty or None if no required fields empty
            output [dict]: Output dict w/ data
        """

        dicts_list = list()
        output = dict()
        empty_required_fields = list()
        alert_children = [
            html.H4("There are missing required fields:", className="alert-heading"),
            html.Hr()
        ]

        for k, v in self.data.items():
            field_value = v['value']
            if v['required'] and (field_value is None or (isinstance(field_value, str) and field_value.isspace()) or field_value == ''):
                empty_required_fields.append(k)
                alert_children.append(html.A(
                    k,
                    href="#" + 'wrapper-' + v['compound_id']['index'] + '-' + v['compound_id']['type'],
                    className="alert-link"
                ))
                alert_children.append(html.Hr())
            if field_value not in ['', None]:
                splited_keys = k.split('-')
                master_key_name = splited_keys[0]
                field_name = splited_keys[-1]

                for element in reversed(splited_keys):
                    if element == field_name:
                        curr_dict = {field_name: v['value']}
                    else:
                        curr_dict = {element: curr_dict}
                    if element == master_key_name:
                        dicts_list.append(curr_dict)

        for e in dicts_list:
            master_key_name = list(e.keys())[0]
            output = SchemaFormContainer._create_nested_dict(data=e, output=output, master_key_name=master_key_name)

        if len(empty_required_fields) > 0:
            return alert_children, output
        else:
            return None, output

    @staticmethod
    def _create_nested_dict(data, output, master_key_name):
        for k, v in data.items():
            if isinstance(v, dict):
                if k == master_key_name and k not in output:
                    output[k] = {}
                    SchemaFormContainer._create_nested_dict(v, output[k], master_key_name)
                elif k != master_key_name and k not in output:
                    output[k] = {}
                    SchemaFormContainer._create_nested_dict(v, output[k], master_key_name)
                else:
                    SchemaFormContainer._create_nested_dict(v, output[k], master_key_name)
            else:
                if isinstance(v, list):
                    element = [e['displayValue'] for e in v]
                else:
                    element = v
                output[k] = element

        return output
