from app.configs.database import db
from sqlalchemy import Column, Integer, ForeignKey


class UserFavoriteAnimeModel(db.Model):

    __tablename__ = 'users_favorites_animes'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    anime_id = Column(Integer, ForeignKey('animes.id'))
