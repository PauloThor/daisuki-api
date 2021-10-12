from flask import Blueprint
from . import user_blueprint

bp = Blueprint('api_bp', __name__, url_prefix='/api')

bp.register_blueprint(user_blueprint.bp)
