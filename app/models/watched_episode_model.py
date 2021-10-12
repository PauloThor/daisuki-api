from dataclasses import dataclass
from app.configs.database import db
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from datetime import datetime


@dataclass
class WatchedEpisodeModel(db.Model):
    watched_at: datetime

    __tablename__ = 'watched_episodes'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    episode_id = Column(Integer, ForeignKey('episodes.id'))
    watched_at = Column(DateTime(timezone=True), nullable=False)
