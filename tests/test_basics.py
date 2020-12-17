

def test_app_is_created(app):
    assert app.name == 'nwb_web_gui'

def test_converter_200(client):
    assert client.get('/converter/').status_code == 200

def test_viewer_200(client):
    assert client.get('/viewer/').status_code == 200

