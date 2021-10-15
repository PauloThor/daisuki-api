from flask import Blueprint
from app.controllers import episode_controller as Controller

bp = Blueprint('episodes', __name__, url_prefix='/episodes')

bp.post('')(Controller.create_episode)
bp.get('')(Controller.get_all_episodes)
bp.put('/views/<int:id>')(Controller.watch_episode)
