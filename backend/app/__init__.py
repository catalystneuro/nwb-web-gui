from flask import Flask
from flask_cors import CORS, cross_origin
import dash
import dash_core_components as dcc
import dash_html_components as html


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile('config.py')
    app.config.update(SEND_FILE_MAX_AGE_DEFAULT=0)

    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    with app.app_context():
        from .index import index
        from .explorer import explorer
        from .custom_dashboards import custom_dashboards

        app.register_blueprint(index.index_bp)
        app.register_blueprint(explorer.explorer_bp)
        app.register_blueprint(custom_dashboards.custom_dashboard_bp)

        dashApp = dash.Dash(
            __name__,
            server=app,
            url_base_pathname='/dashboards/'
        )
        dashApp.layout = html.Div("My Dash app")
        

        return app, dashApp

server, dashApp = create_app()