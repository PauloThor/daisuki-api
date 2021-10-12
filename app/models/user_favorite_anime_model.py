from app.configs.database import db
from sqlalchemy import Column, Integer, ForeignKey
from dataclasses import dataclass
from sqlalchemy.orm import relationship


@dataclass
class UserFavoriteAnimeModel(db.Model):
    anime: str

    __tablename__ = 'users_favorites_animes'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    anime_id = Column(Integer, ForeignKey('animes.id'))

    anime = relationship('AnimeModel')