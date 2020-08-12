import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from pynwb import NWBHDF5IO
from dash.dependencies import Input, Output, State
import dash
from nwbwidgets.dashboards.allen_dash import AllenDashboard
import base64
from pathlib import Path


def make_dashboard(app):
    # dash_app = dash.Dash(
    #     __name__,
    #     title='OEphys Dashboard',
    #     server=server,
    #     routes_pathname_prefix='/dashboard/'
    # )

    # App layout
    layout = html.Div([
        dbc.Row([dbc.Col([
            dcc.Upload(
                id='upload_nwb',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
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
        ],className='col-md-4',)], style={'justify-content': 'center', 'text-align':'center'}),
        html.Div(
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

    @app.callback(
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
                fpath = 'apps/nwbfiles/102086.nwb'
                io = NWBHDF5IO(fpath, mode='r')
                nwb = io.read()
                # Dashboard
                dashboard = AllenDashboard(parent_app=app, nwb=nwb)
                return 'NWB Loaded', dashboard
            else:
                return 'Must be NWB file', ''
        else:
            return '', ''



    '''
    @app.callback(
        Output("uploaded_nwb", "children"),
        [Input("upload_nwb", "contents")],
    )
    def load_nwb(file):
        ctx = dash.callback_context
        source = ctx.triggered[0]['prop_id'].split('.')[0]
        if source == 'upload_nwb':
            return "TODO (load nwb from base64??)"
        else:
            return ''
    '''

    return layout
  
