import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from file_explorer import FileExplorer
from dash.dependencies import Input, Output, State
from datetime import datetime


class Home(html.Div):
    def __init__(self, parent_app):
        super().__init__([])

        self.parent_app = parent_app

        card_converter = [
            dcc.Link(href='/converter', children=[dbc.CardHeader("NWB Converter")], className='cardLink'),
            dbc.CardImg(src="/assets/logo_nwb_square.png", top=True),
            dbc.CardBody(
                children=[
                    html.P(
                        "User friendly metadata edition before converting your data to NWB",
                        className="card-text",
                    ),
                ]
            ),
        ]

        card_viewer = [
            dcc.Link(href='/viewer', children=[dbc.CardHeader("NWB File Viewer")], className='cardLink'),
            dbc.CardImg(src="/assets/logo_nwb_square.png", top=True),
            dbc.CardBody(
                children=[
                    html.P(
                        "Quickly explore your data with interactive NWB widgets",
                        className="card-text",
                    ),
                ]
            ),
        ]

        card_dashboard = [
            dcc.Link(href='/dashboard', children=[dbc.CardHeader("Custom Dashboards")], className='cardLink'),
            dbc.CardImg(src="/assets/logo_nwb_square.png", top=True),
            dbc.CardBody(
                children=[
                    html.P(
                        "Customized Dashboards for NWB files",
                        className="card-text",
                    ),
                ]
            ),
        ]

        card_nwb = [
            html.A(href='https://www.nwb.org/', target='_blank', children=[dbc.CardHeader("Learn NWB")], className='cardLink'),
            dbc.CardImg(src="/assets/logo_nwb_square.png", top=True),
            dbc.CardBody(
                children=[
                    html.P(
                        "Resources to learn more about NWB",
                        className="card-text",
                    ),
                ],
            ),
        ]

        row_of_cards = dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(dbc.Card(card_converter, color="secondary", outline=True), lg=2, md=6),
                        dbc.Col(dbc.Card(card_viewer, color="secondary", outline=True), lg=2, md=6),
                        dbc.Col(dbc.Card(card_dashboard, color="secondary", outline=True), lg=2, md=6),
                        dbc.Col(dbc.Card(card_nwb, color="secondary", outline=True), lg=2, md=6),
                    ],
                    className="mb-4",
                    style={'justify-content': 'center'}
                ),
            ], fluid=True
        )

        """ File Explorer Example """
        file_schema = [{'key': 'nwb_files/example_file.nwb', 'modified': datetime.utcnow(), 'size': 1.5 * 1024 * 1024}]
        explorer = dbc.Container(
            dbc.Row(
                dbc.Col(
                    FileExplorer(
                        id='explorer',
                        value=file_schema
                    ),
                    lg=8
                ),
                style={'justify-content': 'center'}
            ),
            fluid=True
        )

        modal = dbc.Container(
            dbc.Row(
                [
                    dbc.Button("Open File Explorer", id="open"),
                    dbc.Modal(
                        [
                            dbc.ModalHeader("Header"),
                            dbc.ModalBody(explorer),
                            dbc.ModalFooter(
                                dbc.Button("Close", id="close", className="ml-auto")
                            ),
                        ],
                        id="modal",
                        size="xl"
                    ),
                ], style={'justify-content': 'center'}
            )
        )

        self.children = [
            html.Br(),
            html.H1('NWB Web GUI', style={'text-align': 'center'}),
            html.Br(),
            html.Hr(),
            row_of_cards,
            html.Br(),
            modal
        ]

        @self.parent_app.callback(
            Output("modal", "is_open"),
            [Input("open", "n_clicks"), Input("close", "n_clicks")],
            [State("modal", "is_open")],
        )
        def toggle_modal(n1, n2, is_open):
            if n1 or n2:
                return not is_open
            return is_open
