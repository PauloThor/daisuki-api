from app.exc.UserErrors import InvalidPermissionError
from app.models.user_model import UserModel
from datetime import datetime
from flask_jwt_extended import get_jwt_identity


def create_user(data): 
    new_user = UserModel(**data)

    new_user.permission = 'user'
    new_user.created_at = datetime.utcnow()

    return new_user


def verify_admin():
    user_permission = get_jwt_identity()['permission']

    if user_permission != 'admin':
        raise InvalidPermissionError