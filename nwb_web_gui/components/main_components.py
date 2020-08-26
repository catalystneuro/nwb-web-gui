import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output


'''
Collor pallete of icon:
orange: #d17128
grey: #8f8f8f
blue: #114b7c
'''


NAV_LOGO = "assets/logo_nwb.png"


def render_navbar():
    """Make Navbar"""
    navbar = dbc.Navbar(
        [
            dbc.NavLink(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=NAV_LOGO, height="60px")),
                        # dbc.Col(dbc.NavbarBrand("Navbar", className="ml-2")),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="/",
                id="nav_brand"
            ),
            dbc.Nav(
                [
                    dbc.Container([
                        dbc.NavItem(dbc.NavLink(
                            id="nav_nwb_converter", children="NWB Converter", href="converter",
                            style={"font-size": "120%", "font-weight": "normal"}
                        )),
                        dbc.NavItem(dbc.NavLink(
                            id="nav_nwb_viewer", children="NWB Viewer", href="viewer",
                            style={"font-size": "120%", "font-weight": "normal"}
                        )),
                        dbc.NavItem(dbc.NavLink(
                            id="nav_nwb_dashboard", children="Dashboard", href="dashboard",
                            style={"font-size": "120%", "font-weight": "normal"}
                        )),
                        # dbc.NavItem(
                        #     dbc.DropdownMenu(
                        #         children=[
                        #             dbc.DropdownMenuItem("More pages", header=True),
                        #             dbc.DropdownMenuItem("Page 2", href="#"),
                        #             dbc.DropdownMenuItem("Page 3", href="#"),
                        #         ],
                        #         nav=True,
                        #         in_navbar=True,
                        #         label="More",
                        #         toggle_style={"color": "#d17128"},
                        #         toggleClassName="toggle",
                        #         className='toggle'
                        #     )
                        # )
                    ])
                ],
                horizontal='end',
                className="ml-auto flex-nowrap mt-3 mt-md-0"
            )
        ],
        color="dark",
        dark=True
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
