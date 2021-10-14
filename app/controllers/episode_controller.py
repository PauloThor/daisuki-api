from http import HTTPStatus

from app.exc import DuplicatedDataError, InvalidImageError
from app.exc.user_error import InvalidPermissionError
from app.services import episode_service as Episode
from app.services.helpers import encode_json, encode_list_json, paginate
from flask import current_app, jsonify, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequestKeyError


@jwt_required()
def create_episode():
    data = request.form
    session = current_app.db.session

    try:
        new_episode = Episode.upload_episode(request.files, data, session)
        session.add(new_episode)
        session.commit()

        return encode_json(new_episode), HTTPStatus.CREATED
    except InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED
    except InvalidImageError as e:
        return e.message, HTTPStatus.BAD_REQUEST
    except DuplicatedDataError as e:
        return e.message, HTTPStatus.BAD_REQUEST
    except BadRequestKeyError:
        return {'msg': 'Invalid or missing key name. Required options: anime, episodeNumber, image, videoUrl.'}, HTTPStatus.BAD_REQUEST

def get_all_episodes():
    return paginate(Episode.list_episodes()), HTTPStatus.OK


def get_episode(id: int):
    ...


def update_episode_preview():
    ...


@jwt_required()
def update_episode():
    ...


@jwt_required()
def delete_episode():
    ...


@jwt_required()
def create_comment():
    ...


def get_comment():
    ...


@jwt_required()
def delete_comment():
    ...
