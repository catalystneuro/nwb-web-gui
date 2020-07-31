from flask import Blueprint
from flask import current_app as current_app
from app.explorer.views import explorer


explorer_bp = Blueprint(
    'explorer_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

explorer_bp.add_url_rule('/explorer', view_func=explorer, methods=['GET', 'POST'])