from nwbwidgets.utils.timeseries import (timeseries_time_to_ind, get_timeseries_in_units,
                                         get_timeseries_tt)
from tifffile import imread, TiffFile
from pathlib import Path, PureWindowsPath
import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


class AllenDashboard(html.Div):
    def __init__(self, parent_app, nwb):
        super().__init__([])
        self.parent_app = parent_app
        self.nwb = nwb

        if self.nwb is not None:
            # Create traces figure
            self.traces = make_subplots(rows=3, cols=1, row_heights=[0.4, 0.2, 0.4],
                                        shared_xaxes=False, vertical_spacing=0.02)

            # Electrophysiology
            self.ecephys_trace = nwb.processing['ecephys'].data_interfaces['filtered_membrane_voltage']
            self.traces.add_trace(
                go.Scattergl(
                    x=[0],
                    y=[0],
                    line={"color": "black", "width": 1},
                    mode='lines'
                ),
                row=1, col=1
            )

            # Optophysiology
            self.ophys_trace = nwb.processing['ophys'].data_interfaces['fluorescence'].roi_response_series['roi_response_series']
            self.traces.add_trace(
                go.Scattergl(
                    x=[0],
                    y=[0],
                    line={"color": "black", "width": 1},
                    mode='lines'),
                row=3, col=1
            )

            # Layout
            self.traces.update_layout(
                height=400, width=800, showlegend=False, title=None,
                paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)',
                margin=dict(l=60, r=200, t=8, b=20)
            )
            self.traces.update_xaxes(patch={
                'showgrid': False,
                'visible': False,
            })
            self.traces.update_xaxes(patch={
                'visible': True,
                'showline': True,
                'linecolor': 'rgb(0, 0, 0)',
                'title_text': 'time [s]'},
                row=3, col=1
            )
            self.traces.update_yaxes(patch={
                'showgrid': False,
                'visible': True,
                'showline': True,
                'linecolor': 'rgb(0, 0, 0)'
            })
            self.traces.update_yaxes(title_text="Ephys [V]", row=1, col=1)
            self.traces.update_yaxes(title_text="dF/F", row=3, col=1)
            self.traces.update_yaxes(patch={
                "title_text": "Spikes",
                "showticklabels": False,
                "ticks": ""},
                row=2, col=1
            )

        # Dashboard main layout
        self.children = [
            html.H1(
                "Allen OEphys Dashboard",
                style={'text-align': 'center'}
            ),
            html.Hr(),

            html.Div([
                dcc.Slider(
                    id="select_start_time",
                    min=0, max=100, value=0, step=0.05,
                ),
                dcc.Input(
                    id="select_duration",
                    type="number",
                    value=15
                )],
                style={'width': "400px"}
            ),

            html.Br(),

            dcc.Graph(id='figure_traces', figure={})
        ]

        @self.parent_app.callback(
            [Output(component_id='figure_traces', component_property='figure')],
            [Input(component_id='select_start_time', component_property='value'),
             Input(component_id='select_duration', component_property='value')]
        )
        def update_traces(select_start_time, select_duration):
            time_window = [select_start_time, select_start_time + select_duration]

            # Update electrophys trace
            timeseries = self.ecephys_trace
            istart = timeseries_time_to_ind(timeseries, time_window[0])
            istop = timeseries_time_to_ind(timeseries, time_window[1])
            yy, units = get_timeseries_in_units(timeseries, istart, istop)
            xx = get_timeseries_tt(timeseries, istart, istop)
            xrange0, xrange1 = min(xx), max(xx)
            self.traces.data[0].x = xx
            self.traces.data[0].y = list(yy)
            self.traces.update_layout(
                yaxis={"range": [min(yy), max(yy)], "autorange": False},
                xaxis={"range": [xrange0, xrange1], "autorange": False}
            )

            # Update ophys trace
            timeseries = self.ophys_trace
            istart = timeseries_time_to_ind(timeseries, time_window[0])
            istop = timeseries_time_to_ind(timeseries, time_window[1])
            yy, units = get_timeseries_in_units(timeseries, istart, istop)
            xx = get_timeseries_tt(timeseries, istart, istop)
            self.traces.data[1].x = xx
            self.traces.data[1].y = list(yy)
            self.traces.update_layout(
                yaxis3={"range": [min(yy), max(yy)], "autorange": False},
                xaxis3={"range": [xrange0, xrange1], "autorange": False}
            )

            # Update spikes traces
            self.update_spike_traces(time_window=time_window)
            self.traces.update_layout(
                xaxis2={"range": [xrange0, xrange1], "autorange": False}
            )

            return [self.traces]

    def update_spike_traces(self, time_window):
        """Updates list of go.Scatter objects at spike times"""
        self.spike_traces = []
        t_start = time_window[0]
        t_end = time_window[1]
        all_spikes = self.nwb.units['spike_times'][0]
        mask = (all_spikes > t_start) & (all_spikes < t_end)
        selected_spikes = all_spikes[mask]
        # Makes a go.Scatter object for each spike in chosen interval
        for spkt in selected_spikes:
            self.traces.add_trace(go.Scattergl(
                x=[spkt, spkt],
                y=[-1000, 1000],
                line={"color": "gray", "width": .5},
                mode='lines'),
                row=2, col=1
            )
