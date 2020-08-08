from flask import Blueprint
from flask import current_app as current_app
from app.index.views import index, convert_nwb, upload_file, save_metadata, save_all_schemas


index_bp = Blueprint(
    'index_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

index_bp.add_url_rule('/index', view_func=index, methods=['GET', 'POST'])
index_bp.add_url_rule('/index/convertnwb', view_func=convert_nwb, methods=['POST'])
index_bp.add_url_rule('/index/uploadfile', view_func=upload_file, methods=['POST'])
index_bp.add_url_rule('/index/savemetadata', view_func=save_metadata, methods=['POST'])
index_bp.add_url_rule('/index/saveallschemas', view_func=save_all_schemas, methods=['POST'])