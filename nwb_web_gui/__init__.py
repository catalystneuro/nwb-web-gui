from flask import Flask


def init_app():
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile('config.py')
    app.config.update(
        SEND_FILE_MAX_AGE_DEFAULT=0,
    )

    with app.app_context():
        # Import parts of our core Flask app
        from . import routes

        # Import Dash application
        from .dashapps.pages.converter.init_coverter import init_converter
        from .dashapps.pages.viewer.init_viewer import init_viewer
        # from .dashapps.pages.dashboard.init_dashboard import init_dashboard

        init_converter(app)
        init_viewer(app)
        # init_dashboard(app)
        # init_home(app)

        return app
