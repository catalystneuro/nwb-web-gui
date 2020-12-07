import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
from nwb_web_gui.dashapps.components.navbar import render_navbar
from flask.helpers import get_root_path
from pathlib import Path


def init_dashboard(server, dashboard_class):
    FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"
    external_stylesheets = [dbc.themes.BOOTSTRAP, FONT_AWESOME]
    assets = Path(get_root_path(__name__)).parent.parent.parent / 'static'

    dash_app = dash.Dash(
        __name__,
        server=server,
        external_stylesheets=external_stylesheets,
        suppress_callback_exceptions=True,
        routes_pathname_prefix='/dashboard/',
        assets_folder=assets
    )

    navbar = render_navbar()
    # Create Dash Layout
    dash_app.layout = html.Div([navbar, dashboard_class(parent_app=dash_app)])

    return dash_app.server