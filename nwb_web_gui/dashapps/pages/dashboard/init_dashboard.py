import dash
import dash_bootstrap_components as dbc
import dash_html_components as html

from ....dashapps.components.navbar import render_navbar
from ....dashapps.pages.dashboard.dashboard import Dashboard


def init_dashboard(server):
    FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"
    external_stylesheets = [dbc.themes.BOOTSTRAP, FONT_AWESOME]
    dash_app = dash.Dash(
        server=server,
        external_stylesheets=external_stylesheets,
        suppress_callback_exceptions=True,
        routes_pathname_prefix='/dashboard/',
    )

    navbar = render_navbar()
    # Create Dash Layout
    dash_app.layout = html.Div([navbar, Dashboard(parent_app=dash_app)])

    return dash_app.server