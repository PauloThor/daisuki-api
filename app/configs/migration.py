from flask import Flask
from flask_migrate import Migrate


def init_app(app: Flask):

    from app.models.genre_model import GenreModel
    from app.models.anime_model import AnimeModel
    from app.models.genre_anime_model import GenreAnimeModel
    from app.models.episode_model import EpisodeModel
    from app.models.user_model import UserModel
    from app.models.anime_rating_model import AnimeRatingModel
    
    Migrate(app, app.db, compare_type=True)
