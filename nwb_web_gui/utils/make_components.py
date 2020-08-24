import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from datetime import datetime
from file_explorer import FileExplorer
from functools import reduce
import os


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
    """Makes JSON load, save and view buttons"""
    json_buttons = dbc.Container([
        dbc.Row(
            [
                dbc.Col(
                    children=[
                        dcc.Upload(
                            children=dbc.Button('Load JSON', color='dark'),
                            id='load_json_' + id_suffix
                        )
                    ],
                    width={'size': '30px'},
                    style={'margin-left': '10px'}
                ),
                dbc.Col(
                    children=[dbc.Button('Save JSON', color='dark', id='save_json_' + id_suffix)],
                    width={'size': '30px'},
                    style={'margin-left': '10px'}
                ),
                dbc.Col(
                    children=[dbc.Button('Show JSON', color='dark', id='show_json_' + id_suffix)],
                    width={'size': '30px'},
                    style={'margin-left': '10px'}
                ),
            ],
            justify="start",
        ),
    ])

    return json_buttons


def make_modal():
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
                dbc.Modal(
                    [
                        dbc.ModalHeader("Header"),
                        dbc.ModalBody(explorer),
                        dbc.ModalFooter(
                            dbc.Button("Close", id="close_explorer_modal", className="ml-auto")
                        ),
                    ],
                    id="modal_explorer",
                    size="xl"
                ),
            ], style={'justify-content': 'center'}
        )
    )
    return modal


class FileBrowserComponent(html.Div):
    def __init__(self, parent_app, id_suffix):
        super().__init__([])
        self.parent_app = parent_app
        self.id_suffix = id_suffix

        # Button part
        input_group = dbc.InputGroup([
            dbc.InputGroupAddon(
                dbc.Button('Choose NWB file', color='dark', id="button_file_browser_" + id_suffix),
                addon_type="prepend",
            ),
            dbc.Input(id="chosen_nwbfile_" + id_suffix, placeholder="")
        ])

        # Collapsible part - file browser
        self.container = self.make_file_browser()

        self.children = [
            input_group,
            dbc.Collapse(
                dbc.Card(dbc.CardBody(
                    self.container
                )),
                id="collapse_file_browser_" + id_suffix,
            ),
        ]

        @self.parent_app.callback(
            Output("collapse_file_browser_" + id_suffix, "is_open"),
            [Input("button_file_browser_" + id_suffix, "n_clicks")],
            [State("collapse_file_browser_" + id_suffix, "is_open")],
        )
        def toggle_collapse(n, is_open):
            if n:
                return not is_open
            return is_open

    def make_file_browser(self):
        dir_schema = [
            {'key': 'nwb_files/example_file0.nwb', 'modified': datetime.utcnow(), 'size': 1.5 * 1024 * 1024},
            {'key': 'nwb_files/example_file1.nwb', 'modified': datetime.utcnow(), 'size': 1.5 * 1024 * 1024},
            {'key': 'other_files/example_file2.png', 'modified': datetime.utcnow(), 'size': 1.5 * 1024 * 1024},
            {'key': 'other_files/example_file3.jpg', 'modified': datetime.utcnow(), 'size': 1.5 * 1024 * 1024},
        ]
        explorer = dbc.Container(
            dbc.Row(
                dbc.Col(
                    FileExplorer(
                        id='explorer',
                        value=dir_schema
                    ),
                ),
                style={'justify-content': 'left'}
            ),
            fluid=True
        )

        container = dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                explorer
                            ],
                            # className='col-md-4'
                        ),
                    ],
                    # style={'align-items': 'center', 'justify-content': 'center', 'text-align': 'center'}
                )
            ]
        )

        return container

    def make_dict_from_dir(self, rootdir):
        """
        Creates a nested dictionary that represents the folder structure of rootdir
        ref: https://code.activestate.com/recipes/577879-create-a-nested-dictionary-from-oswalk/
        """
        dir = {}
        rootdir = rootdir.rstrip(os.sep)
        start = rootdir.rfind(os.sep) + 1
        for path, dirs, files in os.walk(rootdir):
            folders = path[start:].split(os.sep)
            subdir = dict.fromkeys(files)
            parent = reduce(dict.get, folders[:-1], dir)
            parent[folders[-1]] = subdir
        return dir
