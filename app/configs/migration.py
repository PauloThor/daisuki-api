from flask import Flask
from flask_migrate import Migrate

def init_app(app: Flask):

    from app.models.genre_model import GenreModel
    from app.models.anime_model import AnimeModel
    from app.models.genre_anime_model import genres_animes
    from app.models.episode_model import EpisodeModel
    from app.models.user_model import UserModel
    
    Migrate(app, app.db)

