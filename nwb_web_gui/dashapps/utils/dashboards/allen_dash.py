from nwbwidgets.utils.timeseries import (get_timeseries_maxt, get_timeseries_mint,
                                         timeseries_time_to_ind, get_timeseries_in_units,
                                         get_timeseries_tt)
from tifffile import imread, TiffFile
from pathlib import Path, PureWindowsPath
import numpy as np
import json

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from textwrap import dedent as d


class TimeControllerComponent(html.Div):
    """Controller of start time and duration for time series windows"""
    def __init__(self, parent_app, start=True, duration=True, frame=False,
                 tmin=0, tmax=1, tstart=0, tduration=1):
        super().__init__([])
        self.parent_app = parent_app

        # Start controller
        if start:
            slider_start = dcc.Slider(
                id="slider_start_time",
                min=tmin, max=tmax, value=tstart, step=0.05,
            )

            group_start = dbc.FormGroup(
                [
                    dbc.Label('start (s): ' + str(tstart), id='slider_start_label'),
                    dbc.Col(slider_start)
                ],
            )

            @self.parent_app.callback(
                Output(component_id='slider_start_label', component_property='children'),
                [Input(component_id='slider_start_time', component_property='value')]
            )
            def update_slider_start_label(select_start_time):
                """Updates Start slider controller label"""
                return 'start (s): ' + str(select_start_time)

        # Duration controller
        if duration:
            input_duration = dcc.Input(
                id="input_duration",
                type='number',
                min=.5, max=100, step=.1, value=tduration
            )

            group_duration = dbc.FormGroup(
                [
                    dbc.Label('duration (s):'),
                    dbc.Col(input_duration)
                ],
            )

        # Controllers main layout
        self.children = dbc.Col([
            dbc.FormGroup(
                [
                    dbc.Col(group_start, width=9),
                    dbc.Col(group_duration, width=3)
                ],
                row=True
            )
        ])

        # # Frame controller
        # if frame:
        #     slider_frame = dcc.Slider(
        #         id="slider_frame",
        #         min=tmin, max=tmax, value=tstart, step=0.05,
        #     )
        #     group_frame = dbc.FormGroup(
        #         [
        #             dbc.Label('frame (s): ', id='slider_frame_label'),
        #             dbc.Col(slider_frame)
        #         ],
        #     )
        #
        #     @self.parent_app.callback(
        #         [
        #             Output(component_id='slider_frame', component_property='min'),
        #             Output(component_id='slider_frame', component_property='max'),
        #             Output(component_id='slider_frame', component_property='value')
        #         ],
        #         [
        #             Input(component_id='slider_start_time', component_property='value'),
        #             Input(component_id='input_duration', component_property='value')
        #         ]
        #     )
        #     def update_slider_frame_value(select_start_time, select_duration):
        #         """Updates Frame slider controller value"""
        #         tmin = select_start_time
        #         tmax = select_start_time + select_duration
        #         tframe = (2 * select_start_time + select_duration) / 2
        #
        #         return (
        #             tmin,
        #             tmax,
        #             tframe,
        #         )
        #
        #     @self.parent_app.callback(
        #         Output(component_id='slider_frame_label', component_property='children'),
        #         [Input(component_id='slider_frame', component_property='value')]
        #     )
        #     def update_slider_frame_label(select_frame):
        #         """Updates Frame slider controller label"""
        #         return 'frame (s): ' + str(select_frame)
        # else:
        #     group_frame = []


class TiffImageSeriesComponent(dcc.Graph):
    """Component that renders specific frame of a Tiff file"""
    def __init__(self, parent_app, imageseries, path_external_file=None, pixel_mask=None,
                 foreign_time_window_controller=None, id='tiff_image_series'):
        super().__init__(id=id, figure={}, config={'displayModeBar': False})
        self.parent_app = parent_app
        self.imageseries = imageseries
        self.pixel_mask = pixel_mask
        if foreign_time_window_controller is not None:
            self.time_window_controller = foreign_time_window_controller
        else:
            self.time_window_controller = None

        # Set controller
        if foreign_time_window_controller is None:
            tmin = get_timeseries_mint(imageseries)
            tmax = get_timeseries_maxt(imageseries)
            # self.time_window_controller = StartAndDurationController(tmax, tmin)
        else:
            self.time_window_controller = foreign_time_window_controller

        # Make figure component
        if path_external_file is not None:
            # file_path = imageseries.external_file[0]
            # if "\\" in file_path:
            #     win_path = PureWindowsPath(file_path)
            #     path_ext_file = Path(win_path)
            # else:
            #     path_ext_file = Path(file_path)

            # Get Frames dimensions
            tiff = TiffFile(path_external_file)
            n_samples = len(tiff.pages)
            page = tiff.pages[0]
            n_y, n_x = page.shape

            # Read first frame
            image = imread(path_external_file, key=0)

            self.out_fig = go.Figure(
                data=go.Heatmap(
                    z=image,
                    colorscale='gray',
                    showscale=False,
                )
            )
            self.out_fig.update_layout(
                xaxis=go.layout.XAxis(showticklabels=False, ticks=""),
                yaxis=go.layout.YAxis(showticklabels=False, ticks=""),
            )

        self.figure = self.out_fig


class AllenDashboard(html.Div):
    """Dashboard built with Dash version of NWB widgets"""
    def __init__(self, parent_app, nwb):
        super().__init__([])
        self.parent_app = parent_app
        self.nwb = nwb
        self.controller_time = []

    # def start_dashboard(self):
        if self.nwb is not None:
            # Controllers
            self.controller_time = TimeControllerComponent(
                parent_app=self.parent_app,
                start=True, duration=True, frame=False,
                tmin=0, tmax=100, tstart=0, tduration=10
            )

            # Create traces figure
            self.traces = make_subplots(rows=3, cols=1, row_heights=[0.4, 0.2, 0.4],
                                        shared_xaxes=False, vertical_spacing=0.02)

            # Electrophysiology
            self.ecephys_trace = self.nwb.processing['ecephys'].data_interfaces['filtered_membrane_voltage']
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
            self.ophys_trace = self.nwb.processing['ophys'].data_interfaces['fluorescence'].roi_response_series['roi_response_series']
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
                height=400, showlegend=False, title=None,
                paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)',
                margin=dict(l=60, r=20, t=8, b=20),
                shapes=[{
                    'type': 'line',
                    'x0': 10,
                    'x1': 10,
                    'xref': 'x',
                    'y0': -1000,
                    'y1': 1000,
                    'yref': 'paper',
                    'line': {
                        'width': 4,
                        'color': 'rgb(30, 30, 30)'
                    }
                }]
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

            # Two photon imaging
            self.photon_series = TiffImageSeriesComponent(
                id='figure_photon_series',
                parent_app=self.parent_app,
                imageseries=self.nwb.acquisition['raw_ophys'],
                path_external_file=r"C:\Users\Luiz\Desktop\data_app\oephys_dataset_original\raw_data\Emx1-s_highzoom\102086_2.tif",
                pixel_mask=self.nwb.processing['ophys'].data_interfaces['image_segmentation'].plane_segmentations['plane_segmentation'].pixel_mask[:],
                foreign_time_window_controller=self.controller_time,
            )
            self.photon_series.out_fig.update_layout(
                showlegend=False,
                margin=dict(l=10, r=10, t=70, b=70),
                # width=300, height=300,
            )

        # Dashboard main layout
        self.children = [
            dbc.Container([
                html.H1(
                    "Allen OEphys Dashboard",
                    style={'text-align': 'center'}
                ),
                html.Hr(),
                self.controller_time,
                html.Div([
                    html.Div(
                        dcc.Graph(
                            id='figure_traces',
                            figure={},
                            config={
                                'displayModeBar': False,
                                'edits': {
                                    'shapePosition': True
                                }
                            }
                        ),
                        style={'width': '69%', 'display': 'inline-block'}
                    ),
                    html.Div(
                        self.photon_series,
                        style={'width': '29%', 'display': 'inline-block'}
                    )
                ])
            ])
        ]

        @self.parent_app.callback(
            [Output(component_id='figure_traces', component_property='figure')],
            [
                Input(component_id='slider_start_time', component_property='value'),
                Input(component_id='input_duration', component_property='value')
            ]
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

            # Update frame trace
            self.traces.update_layout(
                shapes=[{
                    'type': 'line',
                    'x0': (xrange1 + xrange0) / 2,
                    'x1': (xrange1 + xrange0) / 2,
                    'xref': 'x',
                    'y0': -1000,
                    'y1': 1000,
                    'yref': 'paper',
                    'line': {
                        'width': 4,
                        'color': 'rgb(30, 30, 30)'
                    }
                }]
            )

            print('here')
            print()
            print(self.traces)

            return [self.traces]

        @self.parent_app.callback(
            [Output(component_id='figure_photon_series', component_property='figure')],
            [Input(component_id='figure_traces', component_property='relayoutData')])
        def change_frame(relayoutData):
            if relayoutData is not None and "shapes[0].x0" in relayoutData:
                pos = relayoutData["shapes[0].x0"]

                # Update image frame
                frame_number = int(pos * self.nwb.acquisition['raw_ophys'].rate)
                # file_path = self.nwb.acquisition['raw_ophys'].external_file[0]
                # if "\\" in file_path:
                #     win_path = PureWindowsPath(file_path)
                #     path_ext_file = Path(win_path)
                # else:
                #     path_ext_file = Path(file_path)

                path_external_file = r"C:\Users\Luiz\Desktop\data_app\oephys_dataset_original\raw_data\Emx1-s_highzoom\102086_2.tif"

                image = imread(path_external_file, key=frame_number)
                self.photon_series.out_fig.data[0].z = image

                return [self.photon_series.out_fig]
            return [{}]

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
