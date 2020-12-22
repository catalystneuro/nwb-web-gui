from flask import render_template, request, redirect
from flask import current_app as app


@app.route('/')
def home():
    """Landing page."""
    return render_template('home.html')


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is not None:
        #raise RuntimeError('Not running with the Werkzeug Server')
        func()
    return


@app.route('/shutdown/', methods=['POST', 'GET'])
def shutdown():
    shutdown_server()
    return 'Server down...'
