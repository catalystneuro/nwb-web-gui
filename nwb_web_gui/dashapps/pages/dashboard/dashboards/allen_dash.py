from nwbwidgets.utils.timeseries import (get_timeseries_maxt, get_timeseries_mint,
                                         timeseries_time_to_ind, get_timeseries_in_units,
                                         get_timeseries_tt)
from tifffile import imread, TiffFile
from pathlib import Path, PureWindowsPath
import numpy as np
import json
from nwbwidgets.ophys import compute_outline

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
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


class TiffImageSeriesDiv(html.Div):
    """Div containing tiff image graph and pixelmask button"""
    def __init__(self, id, parent_app, imageseries, path_external_file=None, pixel_mask=None,
                 foreign_time_window_controller=None):
        super().__init__()

        self.graph = TiffImageSeriesGraphComponent(id=id, parent_app=parent_app, imageseries=imageseries, path_external_file=path_external_file, pixel_mask=pixel_mask,foreign_time_window_controller=foreign_time_window_controller)
        self.pixelmask_btn = dbc.Button('Pixel Mask', id={'type': 'pixelmask_button', 'index': f'mask_btn_{id}'})

        self.children = dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        self.graph, 
                        self.pixelmask_btn
                    ], style={'justify-content': 'center', 'text-align': 'center'}),
                ]),
                width={'size': 12},
            ),
        ])


class TiffImageSeriesGraphComponent(dcc.Graph):
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
            self.tiff = TiffFile(path_external_file)
            self.n_samples = len(self.tiff.pages)
            self.page = self.tiff.pages[0]
            self.n_y, self.n_x = page.shape

            # Read first frame
            self.image = imread(path_external_file, key=0)
        else:
            self.image = []
            self.tiff = None

        self.out_fig = go.Figure(
            data=go.Heatmap(
                z=self.image,
                colorscale='gray',
                showscale=False,
            )
        )
        self.out_fig.update_layout(
            xaxis=go.layout.XAxis(showticklabels=False, ticks=""),
            yaxis=go.layout.YAxis(showticklabels=False, ticks=""),
        )

        self.figure = self.out_fig

    def update_image(self, pos, nwb, relative_path):
        """Update tiff image frame"""

        frame_number = int(pos * nwb.acquisition['raw_ophys'].rate)
        path_external = str(Path(relative_path).parent / Path(nwb.acquisition['raw_ophys'].external_file[0]))
        path_external_file = get_fix_path(path_external)

        if self.tiff is None:
            self.tiff = TiffFile(path_external_file)
            self.n_samples = len(self.tiff.pages)
            self.page = self.tiff.pages[0]
            n_y, n_x = self.page.shape
            self.pixel_mask = nwb.processing['ophys'].data_interfaces['image_segmentation'].plane_segmentations['plane_segmentation'].pixel_mask[:]

            mask_matrix = np.zeros((n_y, n_x))
            for px in self.pixel_mask:
                mask_matrix[px[1], px[0]] = 1

            self.mask_x_coords, self.mask_y_coords = compute_outline(image_mask=mask_matrix, threshold=0.9)

        self.image = imread(path_external_file, key=frame_number)
        self.out_fig.data[0].z = self.image

    def update_pixelmask(self):
        """ Update pixel mask on self figure """

        if len(self.out_fig.data) == 1:
            trace = go.Scatter(
                x=self.mask_x_coords,
                y=self.mask_y_coords,
                fill='toself',
                mode='lines',
                line={"color": "rgb(219, 59, 59)", "width": 4},
            )
            self.out_fig.add_trace(trace)
        else:
            if self.out_fig.data[1].x == self.mask_x_coords and self.out_fig.data[1].y == self.mask_y_coords:
                self.out_fig.data[1].x = []
                self.out_fig.data[1].y = []
            else:
                self.out_fig.data[1].x = self.mask_x_coords
                self.out_fig.data[1].y = self.mask_y_coords


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
                html.Br(),
                dbc.Row(
                    dbc.Col(
                        id='div-controller',
                        children= dbc.Card(
                            self.controller_time, 
                            style={'margin-bottom': '10px', 'padding': '10px'}
                        ),
                        style={'display': 'none'},
                        width={'size': 12},
                    ),
                ),
                dbc.Row([
                    dbc.Col(
                        id='div-figure-traces',
                        children = dbc.Card(
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
                            style={'padding': '30px'}
                        ),
                        style={'display': 'none'},
                        width={'size': 8}
                    ),
                    dbc.Col(
                        id='div-photon-series',
                        style={'display': 'inline-block'},
                        width={'size': 4}
                    ),
                ]),
            ])
        ]

        self.style = {'background-color': '#f0f0f0', 'min-height': '100vh'}

        @self.parent_app.callback(
            [Output(component_id='div-figure-traces', component_property='style'), Output('figure_traces', 'figure')],
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

            return {'display': 'inline-block'}, self.traces

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
            [
                Input(component_id='figure_traces', component_property='relayoutData'),
                Input('figure_traces', 'figure'),
                Input({'type': 'pixelmask_button', 'index': ALL}, 'n_clicks')
            ]
        )
        def change_frame(relayoutData, figure, click):
            """
            Update tiff frame with change on:
              - Figure data
              - Frame selector position
            """

            ctx = dash.callback_context
            trigger_source = ctx.triggered[0]['prop_id'].split('.')[1]

            if trigger_source == 'n_clicks' and click and click[0] is not None:
                self.photon_series.graph.update_pixelmask()
                return [self.photon_series.graph.out_fig]

            if relayoutData is not None and "shapes[0].x0" in relayoutData and trigger_source == 'relayoutData':
                pos = relayoutData["shapes[0].x0"]
            else:
                pos = self.start_frame_x

            self.photon_series.graph.update_image(pos, self.nwb, self.path_nwb)

            return [self.photon_series.graph.out_fig]

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
                line={"color": "#151733", "width": 1},
                mode='lines',
            ),
            row=1, col=1
        )

        # Optophysiology
        self.ophys_trace = self.nwb.processing['ophys'].data_interfaces['fluorescence'].roi_response_series['roi_response_series']
        self.traces.add_trace(
            go.Scattergl(
                x=[0],
                y=[0],
                line={"color": "#151733", "width": 1},
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
        self.photon_series = TiffImageSeriesDiv(
            id='figure_photon_series',
            parent_app=self.parent_app,
            imageseries=self.nwb.acquisition['raw_ophys'],
            path_external_file=None,
            pixel_mask=self.nwb.processing['ophys'].data_interfaces['image_segmentation'].plane_segmentations['plane_segmentation'].pixel_mask[:],
            foreign_time_window_controller=self.controller_time,
        )

        self.photon_series.graph.out_fig.update_layout(
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