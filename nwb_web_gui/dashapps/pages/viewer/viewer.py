from json_schema_to_dash_forms.utils import make_filebrowser_modal, FileBrowserComponent
from flask import current_app as app
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL, MATCH
import dash
from pathlib import Path
from pynwb import NWBHDF5IO
import subprocess
import multiprocessing
from nwbwidgets import nwb2widget
import nbformat as nbf
import os
import time


def call_voila(run_cmd):
    """Call voila processes"""
    subp = subprocess.run(run_cmd, shell=True, capture_output=True)
    print(subp.stdout.decode())


class Viewer(html.Div):
    def __init__(self, parent_app):
        super().__init__([])

        self.parent_app = parent_app
        self.processes_list = []
        self.nwb_file = None

        # Viewer page layout
        self.filebrowser = FileBrowserComponent(parent_app=parent_app, id_suffix='viewer')

        self.children = [
            dbc.Toast(
                id="toast_loadedfile_viewer",
                is_open=False,
                dismissable=False,
                duration=5000
            ),
            html.Br(),
            self.filebrowser,
            html.Br(),
            html.Div(id='voila_div', style={'justify-content': 'center', 'text-align': 'center'}),
        ]

        @self.parent_app.callback(
            [
                Output("toast_loadedfile_viewer", "is_open"),
                Output("toast_loadedfile_viewer", "style"),
                Output("toast_loadedfile_viewer", "children"),
                Output('voila_div', 'children'),
                Output("button_file_browser_viewer", 'n_clicks')
            ],
            [Input('submit-filebrowser-viewer', component_property='n_clicks')],
            [State('chosen-filebrowser-viewer', 'value')]
        )
        def submit_nwb(click, input_value):

            if not click:
                return dash.no_update

            if not any(d['key'] == input_value for d in self.filebrowser.paths_tree):
                # If not selected from explorer
                nwb_path = Path(input_value)
            else:
                # If selected from explorer get absolute path from config
                nwb_path = Path(app.config['NWB_GUI_ROOT_PATH']).parent / Path(input_value)

            style = {
                "position": "fixed", "top": 180, "left": 10, "width": 350,
                "background-color": "#955", "color": "#ffffff", "solid": True
            }
            ctx = dash.callback_context
            source = ctx.triggered[0]['prop_id'].split('.')[0]

            if source == 'submit-filebrowser-viewer':
                if nwb_path.is_file() and str(nwb_path).endswith('.nwb'):
                    self.nwb_path = nwb_path
                    voila_address = self.run_explorer()
                    time.sleep(5)
                    iframe = dbc.Container(html.Iframe(style={"min-width": "100%", 'max-width': '100%', "height": "80vh"}, src=voila_address))
                    style.update({"background-color": "#287836"})
                    return True, style, 'NWB file loaded, widgets started', iframe, 1
                else:
                    style.update({"background-color": "#955"})
                    return True, style, 'Must be a NWB file', '', None
            return False, '', '', '', None

    def kill_processes(self):
        """"""
        if len(self.processes_list) > 0:
            for p in self.processes_list:
                p.terminate()
                p.join()
                p.close()
                print('Terminated: ', p)
            self.processes_list = []

    def run_explorer(self):
        """"""
        self.kill_processes()
        self.aux_notebook = self.create_notebook()

        settings_voila = {'allow_origin': '*', 'headers': {
            'Content-Security-Policy': 'frame-ancestors http://localhost:5000'}}

        run_cmd = ' '.join([
            "voila",
            """ "{}" """.format(str(self.aux_notebook)),
            "--no-browser",
            "--debug",
            "--enable_nbextensions=True",
            "--port=8866",
            "--strip_sources=" + str(True),
            """--Voila.tornado_settings="{}" """.format(settings_voila)
        ])

        proc_voila = multiprocessing.Process(target=call_voila, args=(run_cmd,))
        proc_voila.start()
        self.processes_list.append(proc_voila)
        voila_address = 'http://localhost:8866'

        return voila_address

    def create_notebook(self):
        '''Create aux notebook file for voila render'''

        code = """
            from nwbwidgets import nwb2widget
            import pynwb
            from pathlib import Path
            import os
            fpath = os.path.join(r'""" + str(self.nwb_path) + """')
            io = pynwb.NWBHDF5IO(fpath, 'r', load_namespaces=True)
            nwb = io.read()
            nwb2widget(nwb)
        """

        nb = nbf.v4.new_notebook()
        nb['cells'] = [nbf.v4.new_code_cell(code)]
        fname = 'temp_voila_notebook.ipynb'
        path_aux_notebook = Path.cwd() / fname
        nbf.write(nb, path_aux_notebook)

        return path_aux_notebook
