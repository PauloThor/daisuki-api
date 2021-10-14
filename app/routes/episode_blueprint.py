from flask import Blueprint
from app.controllers.episode_controller import create_episode, delete_episode, get_all_episodes, get_episode, update_episode, update_avatar_episode, delete_episode

bp = Blueprint('episodes', __name__, url_prefix='/episodes')

bp.post('')(create_episode)
bp.get('')(get_all_episodes)
bp.get('/<int:id>')(get_episode)
bp.patch('/<int:id>')(update_episode)
bp.patch('/update-avatar/<int:id>')(update_avatar_episode)
bp.delete('/<int:id>')(delete_episode)