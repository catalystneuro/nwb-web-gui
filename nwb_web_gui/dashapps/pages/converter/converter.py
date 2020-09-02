import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, ALL, MATCH
import dash_bootstrap_components as dbc
import json
from .converter_utils.utils import get_forms_from_schema
from nwb_web_gui.dashapps.utils.make_components import make_modal
from pathlib import Path


class ConverterForms(html.Div):
    def __init__(self, parent_app):
        super().__init__([])
        self.parent_app = parent_app
        self.current_modal_source = ''
        modal = make_modal(parent_app)

        examples_path = Path(__file__).parent.absolute() / 'example_schemas'

        source_schema_path = examples_path / 'source_schema.json'
        with open(source_schema_path, 'r') as inp:
            self.source_json_schema = json.load(inp)

        metadata_schema_path = examples_path / 'metada_schema_2.json'
        with open(metadata_schema_path, 'r') as inp:
            self.metadata_json_schema = json.load(inp)

        metadata_definitions = self.metadata_json_schema['definitions']

        source_forms = get_forms_from_schema(self.source_json_schema, source=True)
        metadata_forms = get_forms_from_schema(self.metadata_json_schema, definitions=metadata_definitions, source=False)

        self.children = [
            dbc.Container([
                dbc.Row(html.H1('NWB Converter'), style={'justify-content': 'center'}),
                dbc.Row([
                    dbc.Col(html.H4('Input Files'), width={'size': 12}, style={'text-align': 'left'}),
                    dbc.Col(source_forms, width={'size': 12}, style={'overflow': 'scroll', 'height': '30vh'}, className='v-scroll'),
                    dbc.Col(
                        dbc.Button('Get Metadata Form', id='get_metadata_btn'),
                        style={'justify-content': 'right', 'text-align': 'right', 'margin-top': '1%'},
                        width={'size': '11'}
                    )
                ]),
                dbc.Row([
                    dbc.Col(html.H4('Metadata'), width={'size': 12}, style={'text-align': 'left'}),
                    dbc.Col(metadata_forms, width={'size': 12}, style={'overflow': 'scroll', 'height': '50vh'}, className='v-scroll')
                ]),
                dbc.Row(modal),
                dbc.Row(
                    dbc.Col(
                        dbc.Button('Run Conversion',id='run_conversion_button') ,width={'size':11}
                    ), style={'text-align':'right', 'margin-top': '1%'}
                ),
            ], style={'min-height': '110vh'})
        ]

        @self.parent_app.callback(
            Output('modal_explorer', 'is_open'),
            [Input({'name': 'source_explorer', 'index': ALL}, 'n_clicks'), Input('close_explorer_modal', 'n_clicks')],
            [State("modal_explorer", "is_open")]
        )
        def open_explorer(click_open, click_close, is_open):

            ctx = dash.callback_context
            source = ctx.triggered[0]['prop_id'].split('.')[0]

            if 'index' in source:
                dict_source = json.loads(source)

                self.current_modal_source = dict_source['index']

            if source != '' and (any(click_open) or click_close):
                return not is_open
            else:
                return is_open

        @self.parent_app.callback(
            Output({'name': 'source_string_input', 'index': MATCH}, 'value'),
            [Input('submit_file_browser_modal', 'n_clicks')],
            [
                State('chosen_file_modal', 'value'),
                State({'name': 'source_string_input', 'index': MATCH}, 'value'),
                State({'name': 'source_string_input', 'index': MATCH}, 'id'),
            ]
        )
        def change_path_values(click, input_value, values, ids):
            ctx = dash.callback_context
            source = ctx.triggered[0]['prop_id'].split('.')[0]

            if self.current_modal_source.replace('explorer', 'input') == ids['index'] and input_value != '':
                return input_value
            else:
                return values
