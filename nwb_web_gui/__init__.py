from flask import Flask

def init_app():
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False)

    with app.app_context():
        # Import parts of our core Flask app
        from . import routes

        # Import Dash application
        from .dashapps.converter.init_converter import init_converter
        from .dashapps.viewer.init_viewer import init_viewer
        from .dashapps.dashboard.init_dashboard import init_dashboard
        #from .dashapps.home.init_home import init_home

        init_converter(app)
        init_viewer(app)
        init_dashboard(app)
        #init_home(app)

        return app