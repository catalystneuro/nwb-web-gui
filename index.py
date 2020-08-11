import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import app, server
from apps.converter import ConverterForms
from apps.viewer import viewer_layout
from apps.dashboard import make_dashboard

from pynwb import NWBHDF5IO
from nwbwidgets.dashboards.allen_dash import AllenDashboard


# Navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink(id="nwb_converter", children="NWB Converter", href="converter")),
        dbc.NavItem(dbc.NavLink(id="nwb_viewer", children="NWB Viewer", href="viewer")),
        dbc.NavItem(dbc.NavLink(id="nwb_dashboard", children="Dashboard", href="dashboard")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="NWB GUI",
    brand_href="#",
    color="primary",
    dark=True,
)

# Initial page layout
app.layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

    # Navbar
    navbar,

    # Page content will be rendered in this element
    html.Div(id='page-content')
])

# Converter layout
converter_layout = ConverterForms(parent_app=app)

# Dashboard layout
# NWB file
fpath = 'apps/nwbfiles/102086.nwb'
io = NWBHDF5IO(fpath, mode='r')
nwb = io.read()

# Dashboard
dashboard_layout = AllenDashboard(parent_app=app, nwb=nwb)


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
