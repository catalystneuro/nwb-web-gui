import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash_cool_components import TagInput, DateTimePicker
from nwb_web_gui.dashapps.utils.make_components import make_filebrowser_modal
import numpy as np
import warnings


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
            'data_type': ''
        }

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
                style={"border": "solid 1px", "border-color": "#ced4da", "border-radius": "5px", "color": '#545057'}
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
                modal_id=modal_id
            )
            # Create internal trigger component and add it to parent Container
            trigger_id = {'type': 'internal-trigger-update-forms-values', 'index': compound_id['index']}
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
            field_input = dbc.Checkbox(
                id=compound_id
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
            self.parent.container.data.update({
                input_id: {
                    'compound_id': compound_id,
                    'owner_class': str(owner_class),
                    'target': value.get('target', None),
                    'value': None,
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
            Output(trigger_id, 'children'),
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
                return str(np.random.rand())
            return ''


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
        self.header = dbc.CardHeader([html.H4(header_text, className="title_" + key)])
        self.body = dbc.CardBody([])
        self.children = [self.header, self.body]

        self.required_fields = schema.get('required', '')

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
                    for i, iv in enumerate(v["items"]):
                        template_name = iv["$ref"].split('/')[-1]
                        schema = self.definitions[template_name]
                        iform = SchemaForm(schema=schema, key=k + f'-{i}', parent_form=self)
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

        # Hidden componentes that serve to trigger callbacks
        self.children_triggers = [
            html.Div(id=id + '-external-trigger-update-forms-values', style={'display': 'none'}),
            html.Div(id=id + '-trigger-update-links-values', style={'display': 'none'}),
            html.Div(id=id + '-output-placeholder-links-values', style={'display': 'none'})
        ]

        # Construct children forms
        self.children_forms = []
        if 'properties' in schema:
            for form_key, form_value in schema['properties'].items():
                iform = SchemaForm(
                    schema=form_value,
                    key=form_key,
                    container=self
                )
                self.children_forms.append(iform)

        self.children = self.children_forms + self.children_triggers

        # Create Outputs for the callback that updates Forms values
        self.update_forms_values_callback_outputs = []
        for v in self.data.values():
            if v['compound_id']['data_type'] != 'link':
                if v['compound_id']['data_type'] == 'boolean':
                    self.update_forms_values_callback_outputs.append(Output(v['compound_id'], 'checked'))
                elif v['compound_id']['data_type'] == 'tags':
                    self.update_forms_values_callback_outputs.append(Output(v['compound_id'], 'injectedTags'))
                else:
                    self.update_forms_values_callback_outputs.append(Output(v['compound_id'], 'value'))
        self.update_forms_values_callback_outputs.append(Output(id + '-trigger-update-links-values', 'children'))

        # Create Outputs for the callback that updates Links values and options
        # An extra paceholder is needed for when there is no link fields
        link_output_options = [Output(v['compound_id'], 'options') for v in self.data.values() if v['compound_id']['data_type'] == 'link']
        link_output_values = [Output(v['compound_id'], 'value') for v in self.data.values() if v['compound_id']['data_type'] == 'link']
        link_output_placeholder = [Output(id + '-output-placeholder-links-values', 'children')]
        self.update_forms_links_callback_outputs = link_output_options + link_output_values + link_output_placeholder

        @self.parent_app.callback(
            self.update_forms_values_callback_outputs,
            [
                Input(self.id + '-external-trigger-update-forms-values', 'children'),
                Input({'type': 'internal-trigger-update-forms-values', 'index': ALL}, 'children')
            ],
            [State(v['compound_id'], 'value') for v in self.data.values() if (v['compound_id']['data_type'] != 'link' and v['compound_id']['data_type'] != 'boolean')] + 
            [State(v['compound_id'], 'checked') for v in self.data.values() if (v['compound_id']['data_type'] != 'link' and v['compound_id']['data_type'] == 'boolean')]

        )
        def update_forms_values(trigger, *states):
            """Updates forms values (except links)"""

            states = states[1:]

            #curr_data = [v['value'] for v in self.data.values() if v['compound_id']['data_type'] != 'link']

            curr_data = list()
            for v in self.data.values():
                if v['compound_id']['data_type'] != 'link':
                    if isinstance(v['value'], list):
                        element = [{"index": i, "displayValue": e} for i, e in enumerate(v['value'])]
                    else:
                        element = v['value']
                    curr_data.append(element)

            if trigger != 'refresh_trigger':
                output = curr_data
                output.append(1)

                return output
            else:
                output = []
                for i, v in enumerate(curr_data):
                    # find a way to generalize this to not depend on a specific trigger
                    if states[i] is not None:
                        output.append(states[i])
                    else:
                        output.append(v)
                output.append(1)

                return output

        @self.parent_app.callback(
            self.update_forms_links_callback_outputs,
            [Input(self.id + '-trigger-update-links-values', 'children')],
            [State(v['compound_id'], 'value') for v in self.data.values() if v['compound_id']['data_type'] == 'name']
        )
        def update_forms_links(trigger, *name_change):
            """
            Updates forms values for links (dropdown options) when names change.
            If a field has a valid value for the 'target' property, this function
            will sweep the data internal dictionary in search for field
            ids ending with '-name' where the 'owner_class' value matches 'target'.
            The resulting list will populate the dropdown menu of the field.

            Example:
            data = {
                'Ecephys-ElectrodeGroup1-device': {
                    'compound_id': {
                        'type': 'metadata-input',
                        'index': 'Ecephys-ElectrodeGroup1-device',
                        'data_type': 'link'
                    }
                    'value': 'device 1',
                    'owner_class': 'pynwb.ecephys.ElectrodeGroup',
                    'target': 'pynwb.device.Device'
                },
                'Ecephys-Device-name': {
                    'compound_id': {
                        'type': 'metadata-input',
                        'index': 'Ecephys-Device-name',
                        'data_type': 'string'
                    }
                    'value': 'device 1',
                    'owner_class': 'pynwb.device.Device',
                    'target': None
                }
            }
            """
            ctx = dash.callback_context
            trigger_source = ctx.triggered[0]['prop_id'].split('.')[0]

            if trigger_source == self.id + '-trigger-update-links-values':
                # Update changed names on backend mapping dictionary
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

                return list_options + list_values + [1]

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
