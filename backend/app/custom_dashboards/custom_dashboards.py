from flask import Blueprint
from flask import current_app as current_app
from app.custom_dashboards.views import custom_dashboard


custom_dashboard_bp = Blueprint(
    'custom_dashboard_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

custom_dashboard_bp.add_url_rule('/custom_dashboard', view_func=custom_dashboard, methods=['GET','POST'])