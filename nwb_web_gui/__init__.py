from flask import Flask
import os
from distutils.util import strtobool


def init_app():
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.ConfigDev')

    # Variables from ENV vars
    app.config['NWB_CONVERTER_MODULE'] = os.environ.get('NWB_CONVERTER_MODULE')
    app.config['NWB_CONVERTER_CLASS'] = os.environ.get('NWB_CONVERTER_CLASS')
    app.config['NWB_DASHBOARD_MODULE'] = os.environ.get('NWB_DASHBOARD_MODULE')
    app.config['NWB_DASHBOARD_CLASS'] = os.environ.get('NWB_DASHBOARD_CLASS')
    app.config['DATA_PATH'] = os.environ.get('DATA_PATH')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['RENDER_CONVERTER'] = bool(strtobool(os.environ.get('RENDER_CONVERTER', 'True')))
    app.config['RENDER_VIEWER'] = bool(strtobool(os.environ.get('RENDER_VIEWER', 'False')))
    app.config['RENDER_DASHBOARD'] = bool(strtobool(os.environ.get('RENDER_DASHBOARD', 'False')))

    with app.app_context():
        # Import parts of our core Flask app
        from . import routes

        # Import NWB converter
        if app.config['NWB_CONVERTER_CLASS'] == 'example':
            from .dashapps.pages.converter.converter_utils.converter_example import ExampleNWBConverter
            converter_class = ExampleNWBConverter
        else:
            import importlib
            converter_class = getattr(
                importlib.import_module(app.config['NWB_CONVERTER_MODULE']),
                app.config['NWB_CONVERTER_CLASS']
            )

        # Import Dash application
        if app.config['RENDER_CONVERTER']:
            from .dashapps.pages.converter.init_coverter import init_converter
            init_converter(server=app, converter_class=converter_class)
        if app.config['RENDER_VIEWER']:
            from .dashapps.pages.viewer.init_viewer import init_viewer
            init_viewer(app)
        if app.config['RENDER_DASHBOARD']:
            from .dashapps.pages.dashboard.init_dashboard import init_dashboard
            init_dashboard(app)

        return app
