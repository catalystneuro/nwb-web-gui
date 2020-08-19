import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from app import app
from apps.converter import ConverterForms
from apps.viewer import Viewer
from apps.dashboard import Dashboard
from apps.home import Home
from components.main_components import render_home


# Create Initial page layout
render_home(app)

# Converter layout
converter_layout = ConverterForms(parent_app=app)

# Dashboard layout
# NWB file
dashboard_layout = Dashboard(parent_app=app)

viewer_layout = Viewer(parent_app=app)

home_layout = Home(parent_app=app)


@app.callback(
    Output('page-content', 'children'),
    [
        Input('url', 'pathname')
    ]
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


if __name__ == '__main__':
    app.run_server(debug=True)
