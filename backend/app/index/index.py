from flask import Blueprint
from flask import current_app as current_app
from app.index.views import index


index_bp = Blueprint(
    'index_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

index_bp.add_url_rule('/index', view_func=index, methods=['GET', 'POST'])