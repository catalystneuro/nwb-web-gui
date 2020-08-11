import dash_core_components as dcc
import dash_html_components as html

from pynwb import NWBHDF5IO
# import dash
from nwbwidgets.dashboards.allen_dash import AllenDashboard


def make_dashboard(app):
    # dash_app = dash.Dash(
    #     __name__,
    #     title='OEphys Dashboard',
    #     server=server,
    #     routes_pathname_prefix='/dashboard/'
    # )

    # NWB file
    fpath = 'apps/nwbfiles/102086.nwb'
    io = NWBHDF5IO(fpath, mode='r')
    nwb = io.read()

    # Dashboard
    dashboard = AllenDashboard(parent_app=app, nwb=nwb)

    # App layout
    layout = html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '60%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        ),

        # dashboard
    ])

    return dashboard
