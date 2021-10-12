from dataclasses import dataclass
from sqlalchemy.sql.schema import ForeignKey
from app.configs.database import db
from sqlalchemy import Column, Integer, ForeignKey
 

@dataclass
class AnimeRatingModel(db.Model):
  rating: int

  __tablename__ = 'animes_ratings'

  id = Column(Integer, primary_key=True)
  rating = Column(Integer, nullable=False)
 
  user_id = Column(Integer, ForeignKey('users.id'))
  anime_id = Column(Integer, ForeignKey('animes.id'))
