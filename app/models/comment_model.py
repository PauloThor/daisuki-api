from dataclasses import dataclass
from app.configs.database import db
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from datetime import datetime


@dataclass
class CommentModel(db.Model):
    id: int
    content: str
    created_at: datetime
    updated_at: datetime

    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    episode_id = Column(Integer, ForeignKey('episodes.id'))
    content = Column(String(511), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
