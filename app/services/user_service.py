from app.exc.user_error import InvalidPermissionError, InvalidRequestError, InvalidUsernameError
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
    new_user.updated_at = datetime.utcnow()

    return new_user


def verify_admin():
    user_permission = get_jwt_identity()['permission']

    if user_permission != 'admin':
        raise InvalidPermissionError


def verify_valid_request_for_token(user, data):
    if 'username' not in data.keys() or 'email' not in data.keys():
        raise InvalidRequestError()

    if not user:
        raise InvalidRequestError()

    if user.username != data['username'] or user.email != data['email']:
        raise InvalidRequestError()