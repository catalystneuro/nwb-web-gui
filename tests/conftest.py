import pytest
from nwb_web_gui import init_app



@pytest.fixture(scope='module')
def app():
    """Instance of main flask app"""
    app = init_app()
    return app
