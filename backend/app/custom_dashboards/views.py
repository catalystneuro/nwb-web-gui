from pynwb import NWBHDF5IO
from nwbwidgets.dashboards.allen_dash import AllenDashboard
from flask import redirect


def custom_dashboard():
    from app import dashApp

    fpath = '/home/vinicius/Área de Trabalho/Trabalhos/neuro/data/102086.nwb'
    io = NWBHDF5IO(fpath, mode='r')
    nwb = io.read()

    dashApp.layout = AllenDashboard(parent_app=dashApp, nwb=nwb)

    return redirect('dashboards')

