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
from dash.dependencies import Input, Output, State
import dash

from textwrap import dedent as d
import pynwb
from nwb_web_gui.dashapps.utils.make_components import FileBrowserComponent


class TimeControllerComponent(html.Div):
    """Controller of start time and duration for time series windows"""
    def __init__(self, parent_app, start=True, duration=True, frame=False,
                 tmin=0, tmax=1, tstart=0, tduration=1):
        super().__init__([])
        self.parent_app = parent_app
        self.tmax = tmax
        self.tmax_duration = tmax

        # Start controller
        if start:
            self.slider_start = dcc.Slider(
                id="slider_start_time",
                min=tmin, max=tmax, value=tstart, step=0.05,
            )

            group_start = dbc.FormGroup(
                [
                    dbc.Label('start (s): ' + str(tstart), id='slider_start_label'),
                    dbc.Col(self.slider_start)
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
            self.input_duration = dcc.Input(
                id="input_duration",
                type='number',
                min=.5, max=100, step=.1, value=tduration
            )

            group_duration = dbc.FormGroup(
                [
                    dbc.Label('duration (s):'),
                    dbc.Col(self.input_duration)
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
            ),
            html.Div(id='external-update-max-time-trigger', style={'display': 'none'})
        ])

        @self.parent_app.callback(
            [Output('input_duration', 'max'), Output('slider_start_time', 'max')],
            [Input('external-update-max-time-trigger', 'children'), Input('input_duration', 'value')],
            [State('input_duration', 'value')]
        )
        def update_max_times(trigger, trigger_duration, duration):
            """
            Update max slider value when duration change
            Update max duration and max slider value when new nwb tmax are defined
            """
            duration_tmax = self.tmax
            slider_tmax = self.tmax - duration

            return duration_tmax, slider_tmax

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
            tiff = TiffFile(path_external_file)
            n_samples = len(tiff.pages)
            page = tiff.pages[0]
            n_y, n_x = page.shape

            # Read first frame
            image = imread(path_external_file, key=0)
        else:
            image = []

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
    def __init__(self, parent_app, path_nwb=None):
        super().__init__([])
        self.parent_app = parent_app
        self.path_nwb = path_nwb
        self.photon_series = []

        # Controllers
        self.controller_time = TimeControllerComponent(
            parent_app=self.parent_app,
            start=True, duration=True, frame=False,
            tmin=0, tmax=100, tstart=0, tduration=10
        )

        self.filebrowser = FileBrowserComponent(parent_app=parent_app, id_suffix='allen-dash')

    # def start_dashboard(self):
        if self.path_nwb is not None:
            self.render_dashboard()

        # Dashboard main layout
        self.children = [
            dbc.Container([
                html.Br(),
                self.filebrowser,
                html.Hr(),
                html.Div(
                    id='div-controller',
                    children=self.controller_time,
                    style={'display': 'none'}
                ),
                html.Div([
                    html.Div(
                        id='div-figure-traces',
                        style={'width': '69%', 'display': 'inline-block'}
                    ),
                    html.Div(
                        id='div-photon-series',
                        style={'width': '29%', 'display': 'inline-block'}
                    )
                ]),
                html.Div(id='hidden')
            ])
        ]

        @self.parent_app.callback(
            Output(component_id='div-figure-traces', component_property='children'),
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
            self.start_frame_x = (xrange1 + xrange0) / 2
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
            graph = dcc.Graph(
                    id='figure_traces',
                    figure=self.traces,
                    config={
                        'displayModeBar': False,
                        'edits': {
                            'shapePosition': True
                        }
                    }
                ),

            return graph

        @self.parent_app.callback(
            [
                Output('button_file_browser_allen-dash', 'n_clicks'), 
                Output('slider_start_time', 'value'), 
                Output('div-controller', 'style'), 
                Output('div-photon-series', 'children'),
                Output('external-update-max-time-trigger', 'children')
            ],
            [Input('submit-filebrowser-allen-dash', component_property='n_clicks')],
            [State('chosen-filebrowser-allen-dash', 'value')]
        )
        def load_nwb_file(click, path):
            if click:
                if Path(path).is_file() and path.endswith('.nwb'):
                    self.path_nwb = path
                    self.render_dashboard()

                    display = {'display': 'block'}
                    self.controller_time.tmax = self.controller_tmax

                    return 1, self.controller_tmin, display, self.photon_series, str(np.random.rand())

        @self.parent_app.callback(
            [Output(component_id='figure_photon_series', component_property='figure')],
            [Input(component_id='figure_traces', component_property='relayoutData')])
        def change_frame(relayoutData):

            if relayoutData is not None and "shapes[0].x0" in relayoutData:
                pos = relayoutData["shapes[0].x0"]
            else:
                pos = self.start_frame_x

            frame_number = int(pos * self.nwb.acquisition['raw_ophys'].rate)
            path_external = str(Path(self.path_nwb).parent / Path(self.nwb.acquisition['raw_ophys'].external_file[0]))
            path_external_file = get_fix_path(path_external)

            image = imread(path_external_file, key=frame_number)
            self.photon_series.out_fig.data[0].z = image

            return [self.photon_series.out_fig]

    def render_dashboard(self):
        io = pynwb.NWBHDF5IO(self.path_nwb, 'r')
        self.nwb = io.read()
        self.controller_tmax = get_timeseries_maxt(self.nwb.processing['ophys'].data_interfaces['fluorescence'].roi_response_series['roi_response_series'])
        self.controller_tmin = get_timeseries_mint(self.nwb.processing['ophys'].data_interfaces['fluorescence'].roi_response_series['roi_response_series'])

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

        path_external = str(Path(self.path_nwb).parent / Path(self.nwb.acquisition['raw_ophys'].external_file[0]))
        path_external = get_fix_path(path_external)

        # Two photon imaging
        self.photon_series = TiffImageSeriesComponent(
            id='figure_photon_series',
            parent_app=self.parent_app,
            imageseries=self.nwb.acquisition['raw_ophys'],
            path_external_file=None,
            pixel_mask=self.nwb.processing['ophys'].data_interfaces['image_segmentation'].plane_segmentations['plane_segmentation'].pixel_mask[:],
            foreign_time_window_controller=self.controller_time,
        )
        self.photon_series.out_fig.update_layout(
            showlegend=False,
            margin=dict(l=10, r=10, t=70, b=70),
            # width=300, height=300,
        )

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


def get_fix_path(path):
    if '\\' in path:
        win_path = PureWindowsPath(path)
        return Path(win_path)
    else:
        return Path(path)