from flask import Flask
import os
from distutils.util import strtobool
import importlib
from .config import config


def init_app(converter_class=None):
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False, template_folder='templates')

    app.config.from_object(config.get(os.environ.get('FLASK_CONFIG') or 'default'))

    # Variables from ENV vars
    app.config['NWB_GUI_CONVERTER_MODULE'] = os.environ.get('NWB_GUI_CONVERTER_MODULE')
    app.config['NWB_GUI_CONVERTER_CLASS'] = os.environ.get('NWB_GUI_CONVERTER_CLASS')
    app.config['NWB_GUI_DASHBOARD_MODULE'] = os.environ.get('NWB_GUI_DASHBOARD_MODULE')
    app.config['NWB_GUI_DASHBOARD_CLASS'] = os.environ.get('NWB_GUI_DASHBOARD_CLASS')
    app.config['NWB_GUI_ROOT_PATH'] = os.environ.get('NWB_GUI_ROOT_PATH')
    app.config['NWB_GUI_SECRET_KEY'] = os.environ.get('NWB_GUI_SECRET_KEY')
    app.config['NWB_GUI_RENDER_CONVERTER'] = bool(strtobool(os.environ.get('NWB_GUI_RENDER_CONVERTER', 'True')))
    app.config['NWB_GUI_RENDER_VIEWER'] = bool(strtobool(os.environ.get('NWB_GUI_RENDER_VIEWER', 'False')))
    app.config['NWB_GUI_RENDER_DASHBOARD'] = bool(strtobool(os.environ.get('NWB_GUI_RENDER_DASHBOARD', 'False')))

    with app.app_context():

        # Import NWB converter
        if converter_class is None:
            if app.config['NWB_GUI_CONVERTER_CLASS'] == 'example':
                from .dashapps.pages.converter.converter_utils.converter_example import ExampleNWBConverter
                converter_class = ExampleNWBConverter
            else:
                converter_class = getattr(
                    importlib.import_module(app.config['NWB_GUI_CONVERTER_MODULE']),
                    app.config['NWB_GUI_CONVERTER_CLASS']
                )

        # Import Dash application
        if app.config['NWB_GUI_RENDER_CONVERTER']:
            from .dashapps.pages.converter.init_coverter import init_converter
            global converter
            converter = init_converter(server=app, converter_class=converter_class)
        if app.config['NWB_GUI_RENDER_VIEWER']:
            from .dashapps.pages.viewer.init_viewer import init_viewer
            global viewer
            init_viewer(app)
        if app.config['NWB_GUI_RENDER_DASHBOARD']:
            from .dashapps.pages.dashboard.init_dashboard import init_dashboard
            dashboard_class = getattr(
                importlib.import_module(app.config['NWB_GUI_DASHBOARD_MODULE']),
                app.config['NWB_GUI_DASHBOARD_CLASS']
            )
            global dashboard
            dashboard = init_dashboard(app, dashboard_class=dashboard_class)

        # Import parts of our core Flask app
        from . import routes

        return app
