from app.exc import InvalidImageError

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}


def check_file_extension(filename: str):
    try:
        file_extension = filename.split('.')[1].lower()
        is_allowed = file_extension in ALLOWED_IMAGE_EXTENSIONS
        if not is_allowed:
            raise InvalidImageError
    except IndexError:
        raise InvalidImageError
