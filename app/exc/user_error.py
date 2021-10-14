class InvalidPasswordError(Exception):
    ...


class InvalidPermissionError(Exception):
    message = {'message': 'Invalid permission'}
    ...


class InvalidUsernameError(Exception):
    ...


class InvalidFavoriteError(Exception):
    ...
