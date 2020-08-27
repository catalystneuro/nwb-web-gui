import dash
import dash_html_components as html
from nwb_web_gui.dashapps.home.home import Home
import dash_bootstrap_components as dbc


def init_home(server):
    FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"
    external_stylesheets = [dbc.themes.BOOTSTRAP, FONT_AWESOME]
    dash_app = dash.Dash(
        server=server,
        external_stylesheets=external_stylesheets,
        suppress_callback_exceptions=True,
        routes_pathname_prefix='/home/',
    )

    # Create Dash Layout
    dash_app.layout = Home(parent_app=dash_app)

    return dash_app.server