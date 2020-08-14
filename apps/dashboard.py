import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from pynwb import NWBHDF5IO
from dash.dependencies import Input, Output, State
import dash
from nwbwidgets.dashboards.allen_dash import AllenDashboard
import base64
from pathlib import Path


class Dashboard(html.Div):
    def __init__(self, parent_app):
        super().__init__([])
        self.parent_app = parent_app

        # Dashboard page layout
        self.children = html.Div([
            dbc.Container([
            dbc.Row([dbc.Col([
                html.Br(),
                dcc.Upload(
                    id='upload_nwb',
                    children=html.Div([
                        'Drag and drop or select NWB file to upload',
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                    },
                    multiple=False
                )
            ], className='col-md-4',)], style={'justify-content': 'center', 'text-align':'center'})]),
            html.Br(),
            dbc.Container(
                [
                    dbc.Row([
                        dbc.Col([
                            dbc.Form(
                            [
                                dbc.FormGroup(
                                    [
                                        dbc.Label("Path to local NWB file"),
                                        dbc.Input(type="text", id='local_nwb', placeholder="Path/to/local.nwb"),
                                    ],
                                ),
                                dbc.Button('Submit', id='submit_nwb'),
                            ],
                        )
                        ], className='col-md-4'),
                    ], style={'align-items': 'center', 'justify-content': 'center', 'text-align':'center'})
                ]),
            html.Div(id='uploaded_nwb', style={'justify-content':'center', 'text-align': 'center'}),
            html.Div(id='dashboard_div', style={'justify-content':'center', 'text-align': 'center'})
        ])

        self.style = {'text-align': 'center', 'justify-content': 'center'}

        @self.parent_app.callback(
            [Output("uploaded_nwb", "children"), Output('dashboard_div', 'children')],
            [Input('submit_nwb', component_property='n_clicks')],
            [State('local_nwb', 'value')]
        )
        def local_nwb(click, input_value):
            ctx = dash.callback_context
            source = ctx.triggered[0]['prop_id'].split('.')[0]

            if source == 'submit_nwb':
                nwb_path = Path(input_value)
                if nwb_path.is_file():
                    # NWB file
                    io = NWBHDF5IO(str(nwb_path), mode='r')
                    nwb = io.read()
                    # Dashboard
                    dashboard = AllenDashboard(parent_app=self.parent_app, nwb=nwb)
                    return 'NWB Loaded', dashboard
                else:
                    return 'Must be NWB file', ''
            else:
                return '', ''
