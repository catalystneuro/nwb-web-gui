import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from datetime import datetime
#from file_explorer import FileExplorer
from dash_cool_components import KeyedFileBrowser
import os
from pathlib import Path
#from nwb_web_gui import FILES_PATH


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


def make_modal(parent_app):
    """ File Explorer Example """
    file_schema = [{'key': 'nwb_files/example_file.nwb', 'modified': datetime.utcnow(), 'size': 1.5 * 1024 * 1024}]
    explorer = FileBrowserComponent(parent_app, 'modal')

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
    def __init__(self, parent_app, id_suffix, root_dir=None):
        super().__init__([])
        self.parent_app = parent_app
        self.id_suffix = id_suffix
        if root_dir is None:
            self.root_dir = '/home/vinicius/Área de Trabalho/Trabalhos/nwb-web-gui/files'
        else:
            self.root_dir = root_dir

        self.make_dict_from_dir()

        # Button part
        input_group = dbc.InputGroup([
            dbc.InputGroupAddon(
                dbc.Button('Choose NWB file', color='dark', id="button_file_browser_" + id_suffix),
                addon_type="prepend",
            ),
            dbc.Input(id="chosen_file_" + id_suffix, placeholder=""),
            dbc.InputGroupAddon(
                dbc.Button('Submit', color='dark', id=f'submit_file_browser_{id_suffix}'),
                addon_type='prepend',
            )
        ])

        # Collapsible part - file browser
        self.container = self.make_file_browser()

        self.children = [
            dbc.Container([
                input_group,
                dbc.Collapse(
                    dbc.Card(dbc.CardBody(
                        self.container
                    )),
                    id="collapse_file_browser_" + id_suffix,
                ),
            ])
        ]

        @self.parent_app.callback(
            [Output("collapse_file_browser_" + id_suffix, "is_open"), Output("chosen_file_" + id_suffix, 'value')],
            [Input("button_file_browser_" + id_suffix, "n_clicks"), Input('explorer', 'selectedPath')],
            [State("collapse_file_browser_" + id_suffix, "is_open")],
        )
        def toggle_collapse(n, path, is_open):
            if path is None:
                path = ''
            if n:
                return not is_open, path
            return is_open, path

    def make_file_browser(self):
        dir_schema = self.paths_tree
        explorer = dbc.Container(
            dbc.Row(
                dbc.Col(
                    KeyedFileBrowser(
                        id='explorer',
                        value=dir_schema
                    ),
                ),
                style={'justify-content': 'left'}
            ),
            fluid=True
        )

        return explorer

    def make_dict_from_dir(self):
        """
        Creates a nested dictionary that represents the folder structure of rootdir
        ref: https://code.activestate.com/recipes/577879-create-a-nested-dictionary-from-oswalk/
        """
        keys_list = []

        for path, dirs, files in os.walk(self.root_dir):
            if len(files) > 0:
                for file in files:
                    aux_dict = {}
                    file_path = Path(path) / file

                    mod_datetime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    delta = datetime.utcnow() - mod_datetime
                    size = os.path.getsize(file_path)

                    aux_dict['key'] = str(file_path).replace("\\", "/")
                    aux_dict['modified'] = delta.days
                    aux_dict['size'] = size

                    keys_list.append(aux_dict)
            elif len(files) == 0 and len(dirs) == 0:
                aux_dict = {}
                aux_dict['key'] = path + '/'
                aux_dict['modified'] = None
                aux_dict['size'] = 0
                keys_list.append(aux_dict)

        self.paths_tree = keys_list
