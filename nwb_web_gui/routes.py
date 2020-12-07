from flask import render_template, request
from flask import current_app as app


@app.route('/')
def home():
    """Landing page."""
    return render_template('home.html')

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['POST', 'GET'])
def shutdown():
    shutdown_server()
    return 'Server down...'
