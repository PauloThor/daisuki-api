from flask import Flask
from flask_migrate import Migrate

def init_app(app: Flask):

    from app.models.anime_model import AnimeModel
    from app.models.user_model import UserModel
    
    Migrate(app, app.db)

