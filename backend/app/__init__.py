from flask import Flask
from flask_cors import CORS, cross_origin


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile('config.py')
    app.config.update(SEND_FILE_MAX_AGE_DEFAULT=0)

    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    with app.app_context():
        from .index import index
        from .explorer import explorer

        app.register_blueprint(index.index_bp)
        app.register_blueprint(explorer.explorer_bp)
        
        return app


server = create_app()
