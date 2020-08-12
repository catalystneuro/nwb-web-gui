import dash_bootstrap_components as dbc
import dash


external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True
)
server = app.server
