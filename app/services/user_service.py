from app.models.user_model import UserModel
from datetime import datetime


def create_user(data): 
    new_user = UserModel(**data)

    new_user.permission = 'user'
    new_user.created_at = datetime.now()

    return new_user
