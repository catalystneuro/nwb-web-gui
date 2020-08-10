from app import server, dashApp
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple


if __name__ == '__main__':
    application = DispatcherMiddleware(server, {'/dash': dashApp.server})
    run_simple('localhost', 5000, application, use_reloader=True, use_debugger=True)