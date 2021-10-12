from dataclasses import dataclass

from sqlalchemy.orm import relationship
from app.configs.database import db
from sqlalchemy import Column, String, Integer


@dataclass
class GenreModel(db.Model):

    name: str

    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)

    animes = relationship('GenreAnimeModel')
