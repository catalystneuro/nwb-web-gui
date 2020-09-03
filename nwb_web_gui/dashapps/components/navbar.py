import dash_html_components as html
import dash_bootstrap_components as dbc


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
            html.A(
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
                        dbc.NavItem(html.A(
                            id="nav_nwb_converter", children="NWB Converter", href="/converter",
                            style={"font-size": "120%", "font-weight": "normal"}, className='nav-link'
                        )),
                        dbc.NavItem(html.A(
                            id="nav_nwb_viewer", children="NWB Viewer", href="/viewer",
                            style={"font-size": "120%", "font-weight": "normal"}, className='nav-link'
                        )),
                        dbc.NavItem(html.A(
                            id="nav_nwb_dashboard", children="Dashboard", href="/dashboard",
                            style={"font-size": "120%", "font-weight": "normal"}, className='nav-link'
                        )),
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