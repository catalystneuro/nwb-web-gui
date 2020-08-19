import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output


NAV_LOGO = "assets/logo_nwb.png"

def render_navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink(id="nav_nwb_converter", children="NWB Converter", href="converter")),
            dbc.NavItem(dbc.NavLink(id="nav_nwb_viewer", children="NWB Viewer", href="viewer")),
            dbc.NavItem(dbc.NavLink(id="nav_nwb_dashboard", children="Dashboard", href="dashboard")),
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
        id="nav_home",
        brand="NWB Web GUI",
        brand_href="home",
        color="info",
        dark=True,
    )

    navbar = dbc.Navbar(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=NAV_LOGO, height="60px")),
                        #dbc.Col(dbc.NavbarBrand("Navbar", className="ml-2")),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="home",
            ),
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink(id="nav_nwb_converter", children="NWB Converter", href="converter")),
                    dbc.NavItem(dbc.NavLink(id="nav_nwb_viewer", children="NWB Viewer", href="viewer")),
                    dbc.NavItem(dbc.NavLink(id="nav_nwb_dashboard", children="Dashboard", href="dashboard")),
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
                horizontal='end'
            )
        ],
        color="dark",
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
