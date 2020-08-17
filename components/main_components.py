import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output


def render_navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink(id="home", children="Home", href="home")),
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
        color="info",
        dark=True,
    )
    return navbar


def render_home(app):
    navbar = render_navbar()
    app.layout = html.Div([
        # represents the URL bar, doesn't render anything
        dcc.Location(id='url', refresh=False),

        # Navbar
        navbar,

        # Page content will be rendered in this element
        html.Div(id='page-content')
    ])
