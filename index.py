import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from app import app
from apps.converter import ConverterForms
from apps.viewer import viewer_layout
from apps.dashboard import Dashboard
from components.main_components import render_home


# Create Initial page layout
render_home(app)

# Converter layout
converter_layout = ConverterForms(parent_app=app)

# Dashboard layout
# NWB file
dashboard_layout = Dashboard(parent_app=app)


@app.callback(
    Output('page-content', 'children'),
    [Input(component_id='nwb_converter', component_property='n_clicks'),
     Input(component_id='nwb_viewer', component_property='n_clicks'),
     Input(component_id='nwb_dashboard', component_property='n_clicks')]
)
def routing(converter, viewer, dashboard):
    ctx = dash.callback_context
    source = ctx.triggered[0]['prop_id'].split('.')[0]
    page = html.H3('Initial page')
    if source == 'nwb_converter':
        page = converter_layout
    elif source == 'nwb_viewer':
        page = viewer_layout
    elif source == 'nwb_dashboard':
        page = dashboard_layout  # make_dashboard(app=app)

    return page


if __name__ == '__main__':
    app.run_server(debug=True)
