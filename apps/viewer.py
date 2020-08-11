import dash_core_components as dcc
import dash_html_components as html


# Viewer page layout
viewer_layout = html.Div([
    html.H1('NWB File Viewer'),
    dcc.RadioItems(
        id='page-2-radios',
        options=[{'label': i, 'value': i} for i in ['Orange', 'Blue', 'Red']],
        value='Orange'
    ),
    html.Div(id='page-2-content'),
    html.Br(),
])
