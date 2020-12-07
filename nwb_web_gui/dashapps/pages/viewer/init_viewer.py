import dash
import dash_html_components as html
from nwb_web_gui.dashapps.pages.viewer.viewer import Viewer
import dash_bootstrap_components as dbc
from nwb_web_gui.dashapps.components.navbar import render_navbar
from dash.dependencies import Input, Output, State, ALL, MATCH
from flask.helpers import get_root_path
from pathlib import Path

def init_viewer(server):
    FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"
    external_stylesheets = [dbc.themes.BOOTSTRAP, FONT_AWESOME]
    assets = Path(get_root_path(__name__)).parent.parent.parent / 'static'

    dash_app = dash.Dash(
        __name__,
        server=server,
        external_stylesheets=external_stylesheets,
        suppress_callback_exceptions=True,
        routes_pathname_prefix='/viewer/',
        assets_folder=assets
    )

    navbar = render_navbar()
    viewer = Viewer(parent_app=dash_app)
    # Create Dash Layout
    dash_app.layout = html.Div([navbar, viewer])

    return dash_app.server