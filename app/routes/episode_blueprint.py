from flask import Blueprint
from app.controllers import episode_controller as Controller

bp = Blueprint('episodes', __name__, url_prefix='/episodes')

bp.post('')(Controller.create_episode)
bp.get('')(Controller.get_all_episodes)
bp.get('/<int:id>')(Controller.get_episode)
bp.patch('/<int:id>')(Controller.update_episode)
bp.patch('/update-avatar/<int:id>')(Controller.update_avatar_episode)
bp.delete('/<int:id>')(Controller.delete_episode)

