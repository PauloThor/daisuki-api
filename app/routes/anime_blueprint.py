from flask import Blueprint
from app.controllers import anime_controller as Controller

bp = Blueprint('animes', __name__, url_prefix='/animes')

bp.post('')(Controller.create)
bp.get('')(Controller.get_animes)
bp.get('/genres')(Controller.get_genres)
bp.get('/genres/<string:genre_name>')(Controller.get_by_genre)
bp.get('/latest')(Controller.get_latest_animes)
bp.patch('/<int:id>')(Controller.update)
bp.patch('/update-avatar/<int:id>')(Controller.update_avatar)
bp.delete('/<int:id>')(Controller.delete)
bp.get('/<anime_name>')(Controller.get_anime_by_name)
bp.put('/<int:id>/ratings')(Controller.set_rating)
bp.get('/most-popular')(Controller.get_most_popular)
bp.get('/<anime_name>/episodes')(Controller.get_anime_episodes)
bp.get('/<anime_name>/<int:episode_number>')(Controller.get_anime_episode_by_number)
bp.get('/search/<string:anime_name>')(Controller.search)
bp.get('/upload-list')(Controller.get_name_animes_incompleted)
