from http import HTTPStatus
from typing import Optional

from flask_jwt_extended.utils import get_jwt_header

from app.exc import DuplicatedDataError, InvalidImageError, PageNotFoundError, DataNotFound
from app.exc.user_error import InvalidPermissionError
from app.models.episode_model import EpisodeModel
from app.models.watched_episode_model import WatchedEpisodeModel
from app.services import episode_service as Episode
from app.services.helpers import encode_json, decode_json, paginate, verify_admin_mod
from app.services.imgur_service import upload_image
from flask import current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import InvalidRequestError
from werkzeug.exceptions import BadRequestKeyError

from datetime import datetime


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
    except DataNotFound as e:
        return e.message, HTTPStatus.NOT_FOUND
    except BadRequestKeyError:
        return {'message': 'Invalid or missing key name. Required options: anime, episodeNumber, image, videoUrl.'}, HTTPStatus.BAD_REQUEST

def get_all_episodes():
    try:
        return paginate(Episode.list_episodes()), HTTPStatus.OK
    except PageNotFoundError as e:
        return e.message, HTTPStatus.UNPROCESSABLE_ENTITY


def get_episode(id: int):
    try:
        return encode_json(Episode.get_episode_by_id(id)), HTTPStatus.OK
    except DataNotFound as e:
        return e.message, HTTPStatus.NOT_FOUND


def update_episode_preview():
    ...


@jwt_required()
def update_episode(id: int):
    try:
        verify_admin_mod()

        data = decode_json(request.json)

        EpisodeModel.query.filter_by(id=id).update(data)
        current_app.db.session.commit()

        return encode_json(Episode.get_episode_by_id(id)), HTTPStatus.OK
    except InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED
    except DataNotFound as e:
        return e.message, HTTPStatus.NOT_FOUND
    except InvalidRequestError as e:
        return {'message': e.args[0].split('\"')[-2] + ' is invalid'}, HTTPStatus.BAD_REQUEST


@jwt_required()
def update_avatar_episode(id: int):
    try:
        verify_admin_mod()

        Episode.get_episode_by_id(id)

        image_url = upload_image(request.files['image'])

        EpisodeModel.query.filter_by(id=id).update({'image_url': image_url})
        current_app.db.session.commit()

        return {'imageUrl': image_url}, HTTPStatus.OK
    except InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED
    except DataNotFound as e:
        return e.message, HTTPStatus.NOT_FOUND
    except InvalidImageError as e:
        return e.message, HTTPStatus.BAD_REQUEST
    except BadRequestKeyError as e:
        return {'message': 'Missing form field image.'}, HTTPStatus.BAD_REQUEST


@jwt_required()
def delete_episode(id: int):
    try:
        verify_admin_mod()

        episode = Episode.get_episode_by_id(id)
        session = current_app.db.session

        session.delete(episode)
        session.commit()

        return encode_json(episode), HTTPStatus.OK
    except InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED
    except DataNotFound as e:
        return e.message, HTTPStatus.NOT_FOUND


@jwt_required()
def create_comment():
    ...


def get_comment():
    ...


@jwt_required()
def delete_comment():
    ...

@jwt_required(optional=True)
def watch_episode(id: int):
    found_user = get_jwt_identity()
    episode = EpisodeModel.query.get(id)

    episode.views += 1
    today = datetime.utcnow()
    session = current_app.db.session

    if found_user:
        watched = WatchedEpisodeModel(user_id=found_user['id'], episode_id=id, watched_at=today)

        session.add(watched)

        return '', HTTPStatus.OK
    
    session.commit()

    return '', HTTPStatus.OK
