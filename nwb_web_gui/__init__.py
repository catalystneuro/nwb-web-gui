from flask import Flask
import os
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash
from dash.dependencies import Input, Output

from nwb_web_gui.converter import ConverterForms
from nwb_web_gui.viewer import Viewer
from nwb_web_gui.dashboard import Dashboard
from nwb_web_gui.home import Home
from nwb_web_gui.components.main_components import render_home


PUBLIC_IP = os.getenv('PUBLIC_IP')
PUBLIC_IP = '0.0.0.0'


def create_dash_app():

    """Create Flask application."""
    server = Flask(__name__, instance_relative_config=False)
    server.config.from_pyfile('config.py')
    server.config.update(
        PUBLIC_IP=PUBLIC_IP,
    )

    with server.app_context():
        FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"
        external_stylesheets = [dbc.themes.BOOTSTRAP, FONT_AWESOME]
        dash_app = dash.Dash(
            __name__,
            external_stylesheets=external_stylesheets,
            suppress_callback_exceptions=True,
            server=server,
            title='NWB GUI'
        )

        dash_app.enable_dev_tools(debug=True)

        # Create Initial page layout
        render_home(dash_app)

        # Home page layout
        home_layout = Home(parent_app=dash_app)

        # Converter layout
        converter_layout = ConverterForms(parent_app=dash_app)

        # NWB File Viewerlayout
        viewer_layout = Viewer(parent_app=dash_app)

        # Dashboard layout
        dashboard_layout = Dashboard(parent_app=dash_app)

        # Routing callback
        @dash_app.callback(
            Output('page-content', 'children'),
            [Input('url', 'pathname')]
        )
        def routing(pathname):

            page = home_layout
            if pathname == '/':
                converter_layout.clean_converter_forms()
                page = home_layout
            elif pathname == '/converter':
                page = converter_layout
            elif pathname == '/viewer':
                converter_layout.clean_converter_forms()
                page = viewer_layout
            elif pathname == '/dashboard':
                converter_layout.clean_converter_forms()
                page = dashboard_layout
            else:
                converter_layout.clean_converter_forms()
                page = html.Div([html.H1('Page not found')])

            return page

        return dash_app


dash_app = create_dash_app()
