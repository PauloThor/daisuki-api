from flask import Blueprint
from app.controllers.episode_controller import create_episode, get_all_episodes

bp = Blueprint('episodes', __name__, url_prefix='/episodes')

bp.post('')(create_episode)
bp.get('')(get_all_episodes)