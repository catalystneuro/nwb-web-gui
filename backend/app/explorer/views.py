from flask import jsonify, render_template, request, redirect, url_for
from pathlib import Path
from flask import current_app as app
import subprocess
import multiprocessing
from pynwb import NWBHDF5IO
from nwbwidgets import nwb2widget
import nbformat as nbf
import os

processes_list = []
nwb_file = None

def create_notebook(nwbpath):
    '''Create aux notebook file for voila render'''

    code = """
    from nwbwidgets import nwb2widget
    import pynwb
    from pathlib import Path
    import os
    fpath = os.path.join(r'""" + str(nwbpath) + """')
    io = pynwb.NWBHDF5IO(fpath, 'r', load_namespaces=True)
    nwb = io.read()
    nwb2widget(nwb)
    """

    nb = nbf.v4.new_notebook()
    nb['cells'] = [nbf.v4.new_code_cell(code)]
    fname = 'temp_nb.ipynb'
    path_aux_notebook = Path(app.root_path) / 'explorer' / fname
    nbf.write(nb, path_aux_notebook)

    return path_aux_notebook

def call_voila(run_cmd):
    ''' Call voila processes'''
    subp = subprocess.run(run_cmd, shell=True, capture_output=True)
    print(subp.stdout.decode())


def kill_processes():
    global processes_list

    if len(processes_list) > 0:
        for p in processes_list:
            p.terminate()
            p.join()
            p.close()
            print('Terminated: ', p)
        processes_list = []


def check_exit():
    global nwb_file

    if request.method == 'POST' and 'exitApp' in request.form:
        kill_processes()

        nwb_file = None
        if request.form['exitApp'] == 'dashboard':
            return 'http://localhost:3000/custom_dashboard'
        else:
            return 'http://localhost:3000/'
    else:
        return 'continue'


def explorer():
    '''Explorer route main function '''

    global processes_list
    global nwb_file

    if request.method == 'POST' and 'myfile' in request.form and request.form['myfile'] != '':
        nwb_file = request.form['myfile']
        if len(processes_list) > 0:
            kill_processes()

    if nwb_file is None:
        render_iframe = False
        leave_app = check_exit()
        if leave_app != 'continue':
            return redirect(leave_app)
    else:
        render_iframe = True
        # First, check if it an exit call
        leave_app = check_exit()
        if leave_app != 'continue':
            return redirect(leave_app)

        # path_notebook = Path(app.root_path) / 'explorer/explorer.ipynb'
        aux_notebook = create_notebook(nwb_file)

        settings_voila = {'allow_origin': '*', 'headers': {
            'Content-Security-Policy': 'frame-ancestors http://localhost:5000'}}

        run_cmd = ' '.join([
            "voila",
            """ "{}" """.format(str(aux_notebook)),
            "--no-browser",
            "--enable_nbextensions=True",
            "--port=8866",
            "--strip_sources=" + str(True),
            """--Voila.tornado_settings="{}" """.format(settings_voila)
        ])

        proc_voila = multiprocessing.Process(target=call_voila, args=(run_cmd,))
        proc_voila.start()
        processes_list.append(proc_voila)
        voila_address = 'http://localhost:8866'

    voila_address = 'http://localhost:8866'

    return render_template('explorer/explorer.html', voila_address=voila_address, render_iframe=render_iframe)
