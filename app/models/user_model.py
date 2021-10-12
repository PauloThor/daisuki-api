from dataclasses import dataclass
from datetime import datetime
from app.configs.database import db
from sqlalchemy import Column, String, Integer, DateTime
from werkzeug.security import generate_password_hash, check_password_hash

from app.exc.UserErrors import InvalidPasswordError


@dataclass
class UserModel(db.Model):
 
    id: int
    email: str
    username: str
    avatar_url: str
    permission: str
    created_at: datetime

    __tablename__ = 'users'
 

    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    username = Column(String(50), nullable=False, unique=True)
    avatar_url = Column(String(255))
    permission = Column(String(30), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    password_hash = Column(String(511), nullable=False)
  

    @property
    def password(self):
        raise AttributeError("Password cannot be accessed!")


    @password.setter
    def password(self, password_to_hash):
        self.password_hash = generate_password_hash(password_to_hash)


    def verify_password(self, password_to_compare):
        is_valid = check_password_hash(self.password_hash, password_to_compare)
        if not is_valid:
            raise InvalidPasswordError 
