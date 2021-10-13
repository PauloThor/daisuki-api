from app.exc import InvalidImageError
from app.exc.user_error import InvalidPermissionError
from flask_jwt_extended import get_jwt_identity

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}


def check_file_extension(filename: str):
    try:
        file_extension = filename.split('.')[1].lower()
        is_allowed = file_extension in ALLOWED_IMAGE_EXTENSIONS
        if not is_allowed:
            raise InvalidImageError
    except IndexError:
        raise InvalidImageError


def verify_admin_mod():
    user_permission = get_jwt_identity()['permission']

    if user_permission != 'admin' and user_permission != 'mod':
        raise InvalidPermissionError
