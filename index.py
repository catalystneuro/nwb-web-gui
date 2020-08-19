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
        Input(component_id='nav_nwb_converter', component_property='n_clicks'),
        Input(component_id='nav_nwb_viewer', component_property='n_clicks'),
        Input(component_id='nav_nwb_dashboard', component_property='n_clicks'),
        Input(component_id='nav_brand', component_property='n_clicks')
    ]
)
def routing(converter, viewer, dashboard, home):
    ctx = dash.callback_context
    source = ctx.triggered[0]['prop_id'].split('.')[0]
    page = home_layout
    if source == 'nav_nwb_converter':
        page = converter_layout
    elif source == 'nav_nwb_viewer':
        page = viewer_layout
    elif source == 'nav_nwb_dashboard':
        page = dashboard_layout  # make_dashboard(app=app)
    elif source == 'nav_brand':
        page = home_layout

    return page


if __name__ == '__main__':
    app.run_server(debug=True)
