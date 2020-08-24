from nwb_web_gui.dashboards.allen_dash import AllenDashboard
from nwb_web_gui.utils.make_components import make_file_picker

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash

from pynwb import NWBHDF5IO
from pathlib import Path


class Dashboard(html.Div):
    def __init__(self, parent_app):
        super().__init__([])
        self.parent_app = parent_app

        # Dashboard page layout
        filepicker = make_file_picker(id_suffix='dashboard')
        dashboard = AllenDashboard(parent_app=self.parent_app, nwb=None)

        self.children = html.Div([
            html.Br(),
            filepicker,
            html.Div(id='uploaded_nwb', style={'justify-content': 'center', 'text-align': 'center'}),
            html.Div(id='dashboard_div', style={'justify-content': 'center', 'text-align': 'center'})
        ])

        self.style = {'text-align': 'center', 'justify-content': 'center'}

        @self.parent_app.callback(
            [Output("uploaded_nwb", "children"), Output('dashboard_div', 'children')],
            [Input('submit_nwb_dashboard', component_property='n_clicks')],
            [State('nwb_dashboard', 'value')]
        )
        def local_nwb(click, input_value):
            ctx = dash.callback_context
            source = ctx.triggered[0]['prop_id'].split('.')[0]

            if source == 'submit_nwb_dashboard':
                nwb_path = Path(input_value)
                if nwb_path.is_file():
                    # NWB file
                    io = NWBHDF5IO(str(nwb_path), mode='r')
                    nwbfile = io.read()
                    # Dashboard
                    dashboard = AllenDashboard(parent_app=self.parent_app, nwb=nwbfile)
                    return 'NWB Loaded', dashboard
                else:
                    return 'Must be NWB file', ''
            else:
                return '', ''
