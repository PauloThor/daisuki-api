from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import relationship
from app.configs.database import db
from sqlalchemy import Column, String, Integer, Boolean, DateTime


@dataclass
class AnimeModel(db.Model):
   id: int
   name: str
   synopsis: str
   image_url: str
   total_episodes: int
   is_movie: bool
   is_dubbed: bool
   is_completed: bool
   created_at: datetime
 
   __tablename__ = 'animes'
 
  
   id = Column(Integer, primary_key=True)
   name = Column(String(255), nullable=False, unique=True)
   synopsis = Column(String(1023), nullable=False)
   image_url = Column(String(255), nullable=False)
   total_episodes = Column(Integer, nullable=False)
   is_movie = Column(Boolean, nullable=False)
   is_dubbed = Column(Boolean, nullable=False)
   is_completed = Column(Boolean, nullable=False)
   created_at = Column(DateTime(timezone=True), nullable=False)

   users_favorited = db.relationship('UserFavoriteAnimeModel', cascade='all, delete')
   
   genres = relationship('GenreAnimeModel')
