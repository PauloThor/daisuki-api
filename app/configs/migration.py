from flask import Flask
from flask_migrate import Migrate

def init_app(app: Flask):

    from app.models.anime_model import AnimeModel

    Migrate(app, app.db)

