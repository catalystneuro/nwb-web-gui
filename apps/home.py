import dash_html_components as html
import dash_bootstrap_components as dbc


class Home(html.Div):
    def __init__(self, parent_app):
        super().__init__([])

        self.parent_app = parent_app

        card_converter = [
            dbc.CardHeader("Converter Forms"),
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
            dbc.CardHeader("NWB File Viewer"),
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
            dbc.CardHeader("Dashboard"),
            dbc.CardBody(
                children=[
                    html.P(
                        "Customized Dashboards",
                        className="card-text",
                    ),
                ]
            ),
        ]

        card_nwb = [
            dbc.CardHeader("Learn NWB"),
            dbc.CardBody(
                children=[
                    html.P(
                        "Resources to learn more about NWB",
                        className="card-text",
                    ),
                ]
            ),
        ]

        row_of_cards = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(dbc.Card(card_converter, color="secondary", outline=True)),
                        dbc.Col(dbc.Card(card_viewer, color="secondary", outline=True)),
                        dbc.Col(dbc.Card(card_dashboard, color="secondary", outline=True)),
                        dbc.Col(dbc.Card(card_nwb, color="secondary", outline=True)),
                    ],
                    className="mb-4",
                ),
            ]
        )

        self.children = [
            html.H1('NWB Web GUI', className='header'),
            html.Br(),
            html.Hr(),
            row_of_cards
        ]
