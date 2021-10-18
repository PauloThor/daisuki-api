from dataclasses import dataclass
from app.configs.database import db
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from datetime import datetime


@dataclass
class EpisodeModel(db.Model):
    id: int
    anime_id: int
    episode_number: int
    image_url: str
    video_url: str
    views: int
    created_at: datetime
    updated_at: datetime

    __tablename__ = 'episodes'

    id = Column(Integer, primary_key=True)
    anime_id = Column(Integer, ForeignKey('animes.id'))
    episode_number = Column(Integer, nullable=False)
    image_url = Column(String(255), nullable=False)
    video_url = Column(String(255), nullable=False)
    views = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    viewers = relationship('UserModel', backref='watched', secondary='watched_episodes')
    comments = relationship('CommentModel', cascade='all, delete-orphan')
