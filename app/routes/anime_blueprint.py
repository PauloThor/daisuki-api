from flask import Blueprint
from app.controllers.anime_controller import create

bp = Blueprint('animes', __name__, url_prefix='/animes')

bp.post('')(create)
