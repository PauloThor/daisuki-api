from app.configs.database import db
from sqlalchemy import Column, Integer
from sqlalchemy.sql.schema import ForeignKey


class GenreAnimeModel(db.Model):

    __tablename__ = 'genres_animes'

    id = Column(Integer, primary_key=True)
    genre_id = Column(Integer, ForeignKey('genres.id'))
    anime_id = Column(Integer, ForeignKey('animes.id'))
