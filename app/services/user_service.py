from app.exc.UserErrors import InvalidPermissionError, InvalidUsernameError
from app.models.user_model import UserModel
from datetime import datetime
from flask_jwt_extended import get_jwt_identity


def create_user(data): 
    email = data.pop('email')

    new_user = UserModel(**data)

    username = new_user.username

    users = UserModel.query.filter(UserModel.username.ilike(username)).all()

    if len(users) > 0:
        raise InvalidUsernameError
    


    new_user.permission = 'user'
    new_user.email = email.lower()
    new_user.created_at = datetime.utcnow()

    return new_user


def verify_admin():
    user_permission = get_jwt_identity()['permission']

    if user_permission != 'admin':
        raise InvalidPermissionError