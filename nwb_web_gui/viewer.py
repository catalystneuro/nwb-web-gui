from .utils.make_components import make_file_picker, FileBrowserComponent

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash
from pathlib import Path
from pynwb import NWBHDF5IO
import subprocess
import multiprocessing
from nwbwidgets import nwb2widget
import nbformat as nbf
import os
from nwb_web_gui import FILES_PATH


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
        # filepicker = make_file_picker(id_suffix='voila')
        direxplorer = FileBrowserComponent(parent_app=parent_app, id_suffix='viewer', root_dir=FILES_PATH)

        self.children = [
            html.Br(),
            # filepicker,
            direxplorer,
            html.Br(),
            html.Div(id='uploaded_voila_nwb', style={'justify-content': 'center', 'text-align': 'center'}),
            html.Div(id='voila_div', style={'justify-content': 'center', 'text-align': 'center'})
        ]

        @self.parent_app.callback(
            [
                Output("uploaded_voila_nwb", "children"),
                Output('voila_div', 'children')
            ],
            [Input('submit_file_browser_viewer', component_property='n_clicks')],
            [State('chosen_file_viewer', 'value')]
        )
        def submit_nwb(click, input_value):

            ctx = dash.callback_context
            source = ctx.triggered[0]['prop_id'].split('.')[0]

            if source == 'submit_file_browser_viewer':
                nwb_path = Path(input_value)
                if nwb_path.is_file() and str(nwb_path).endswith('.nwb'):
                    self.nwb_path = nwb_path
                    voila_address = self.run_explorer()
                    iframe = html.Iframe(style={"min-width": "100vw", 'max-width': '100vw', "min-height": "100vh"}, src=voila_address)

                    return 'NWB Loaded', iframe
                else:
                    return 'Must be NWB file', ''

            return '', ''

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
            'Content-Security-Policy': 'frame-ancestors http://localhost:8050'}}

        run_cmd = ' '.join([
            "voila",
            """ "{}" """.format(str(self.aux_notebook)),
            "--no-browser",
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
