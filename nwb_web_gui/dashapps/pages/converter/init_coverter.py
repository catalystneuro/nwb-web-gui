import dash
import dash_html_components as html
from nwb_web_gui.dashapps.pages.converter.converter import ConverterForms
import dash_bootstrap_components as dbc
from nwb_web_gui.dashapps.components.navbar import render_navbar


def init_converter_new(server):
    FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"
    external_stylesheets = [dbc.themes.BOOTSTRAP, FONT_AWESOME]
    dash_app = dash.Dash(
        server=server,
        external_stylesheets=external_stylesheets,
        suppress_callback_exceptions=True,
        routes_pathname_prefix='/converter/',
    )

    navbar = render_navbar()
    # Create Dash Layout
    dash_app.layout = html.Div([navbar, ConverterForms(parent_app=dash_app)])

    return dash_app.server