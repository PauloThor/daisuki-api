from dataclasses import asdict
from math import ceil

import humps
from app.exc import InvalidImageError, PageNotFoundError
from app.exc.user_error import InvalidPermissionError
from flask import jsonify, request
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


def paginate(data_list, per_page=12, page=1):
        per_page = int(request.args.get('per_page', per_page))
        page = int(request.args.get('page', page))
        last_page = ceil(len(data_list)/per_page)

        if last_page == 0:
            return {
                "page": page,
                "previous": None,
                "next": None,
                "data": []
            }

        if page < 1 or page > last_page:
            raise PageNotFoundError(page)

        previous_page = None
        next_page = None

        if page < last_page:
            next_page = page + 1
        
        if page > 1:
            previous_page = page - 1
        
        data_list = [humps.camelize(asdict(data)) for data in data_list]
        
        return {
            "page": page,
            "previous": f'page={previous_page}&per_page={per_page}' if previous_page else previous_page,
            "next": f'page={next_page}&per_page={per_page}' if next_page else next_page,
            "data": data_list[((page-1)*per_page):(page*per_page)]
        }


def decode_json(data: dict) -> dict:
    return humps.decamelize(data)


def encode_json(model) -> dict: 
    data = asdict(model)
    return jsonify(humps.camelize(data))


def encode_list_json(data: list) -> list:
    output = [humps.camelize(asdict(model)) for model in data]
    return jsonify(output)
