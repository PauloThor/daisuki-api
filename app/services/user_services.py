from app.models.user_model import UserModel
from datetime import datetime


def create_user(data): 
    password_to_hash = data.pop('password')

    new_user = UserModel(**data)

    new_user.password = password_to_hash
    new_user.permission = 'user'
    new_user.created_at = datetime.now()

    return new_user
