from flask import Blueprint
from app.controllers import anime_controller as Controller

bp = Blueprint('animes', __name__, url_prefix='/animes')

bp.post('')(Controller.create)
bp.get('')(Controller.get_animes)
bp.patch('/<int:id>')(Controller.update)
bp.patch('/update-avatar/<int:id>')(Controller.update_avatar)
bp.delete('/<int:id>')(Controller.delete)
bp.put('/<int:id>/ratings')(Controller.set_rating)
bp.get('/most-popular')(Controller.get_most_popular)
