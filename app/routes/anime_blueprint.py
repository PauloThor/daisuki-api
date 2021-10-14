from flask import Blueprint
from app.controllers import anime_controller as Controller

bp = Blueprint('animes', __name__, url_prefix='/animes')

bp.post('')(Controller.create)
bp.get('')(Controller.get_animes)
bp.get('/latest')(Controller.get_latest_animes)
bp.patch('/<int:id>')(Controller.update)
bp.patch('/update-avatar/<int:id>')(Controller.update_avatar)
bp.delete('/<int:id>')(Controller.delete)
bp.put('/<int:id>/ratings')(Controller.create_or_update_rating)
