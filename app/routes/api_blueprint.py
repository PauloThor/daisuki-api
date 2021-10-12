from flask import Blueprint
from . import anime_blueprint

bp = Blueprint('api_bp', __name__, url_prefix='/api')

bp.register_blueprint(anime_blueprint.bp)
