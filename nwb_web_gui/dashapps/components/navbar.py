import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from flask import current_app as app


'''
Collor pallete of icon:
orange: #d17128
grey: #8f8f8f
blue: #114b7c
'''

NAV_LOGO = "assets/logo_nwb.png"


def render_navbar():
    """Make Navbar"""
    apps_dict = {
        'converter': {
            'render': app.config['NWB_GUI_RENDER_CONVERTER'],
            'id': 'nav_nwb_converter',
            'children': 'NWB Converter',
            'href': '/converter'
        },
        'viewer': {
            'render': app.config['NWB_GUI_RENDER_VIEWER'],
            'id': 'nav_nwb_viewer',
            'children': 'NWB Viewer',
            'href': '/viewer'
        },
        'dashboard': {
            'render': app.config['NWB_GUI_RENDER_DASHBOARD'],
            'id': 'nav_nwb_dashboard',
            'children': 'Dashboard',
            'href': '/dashboard'
        },
        "close_gui": {
            "render": True,
            'id': "close_gui",
            "children": "Close GUI",
            "href": '/shutdown'
        }
    }

    navchildren = []
    for k, v in apps_dict.items():
        if v['render']:
            item = dbc.NavItem(html.A(
                            id=v['id'], children=v['children'], href=v['href'],
                            style={"font-size": "120%", "font-weight": "normal"}, className='nav-link'
                    ))
            navchildren.append(item)

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
                    dbc.Container(
                        navchildren
                    )
                ],
                horizontal='end',
                className="ml-auto flex-nowrap mt-3 mt-md-0"
            )
        ],
        color="dark",
        dark=True
    )

    return navbar
