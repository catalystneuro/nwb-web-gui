import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


def make_file_picker(id_suffix):
    filepicker = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Form(
                                [
                                    dbc.FormGroup(
                                        [
                                            dbc.Label("Choose NWB file:"),
                                            dbc.Input(
                                                type="text", id='nwb_' + id_suffix,
                                                placeholder="Path/to/local.nwb"
                                            ),
                                        ],
                                    ),
                                    dbc.Button('Submit', id='submit_nwb_' + id_suffix),
                                ],
                            )
                        ],
                        className='col-md-4'
                    ),
                ],
                style={'align-items': 'center', 'justify-content': 'center', 'text-align': 'center'}
            )
        ]
    )

    return filepicker


def make_upload_file(id_suffix):
    uploader = dbc.Container([
        dbc.Row([
            dbc.Col([
                dcc.Upload(
                    id=id_suffix,
                    children=html.Div(
                        ["Drag and drop or click to select a file to upload."],
                    ),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                    },
                    multiple=False,
                ),
            ], className='col-md-4')],
            style={'justify-content': 'center'}
        )
    ])

    return uploader


def make_json_file_buttons(id_suffix):
    """Makes JSON load and save buttons"""
    json_buttons = dbc.Container([
        dbc.Row(
            [
                dbc.Col(
                    children=[
                        dcc.Upload(
                            children=dbc.Button('Load JSON'),
                            id='load_json_' + id_suffix
                        )
                    ],
                    width={'size': '30px'},
                    style={'margin-left': '10px'}
                ),
                dbc.Col(
                    children=[dbc.Button('Save JSON', id='save_json_' + id_suffix)],
                    width={'size': '30px'},
                    style={'margin-left': '10px'}
                ),
            ],
            justify="start",
        ),
    ])

    return json_buttons
