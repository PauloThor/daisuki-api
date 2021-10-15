from http import HTTPStatus
from typing import Optional

from flask_jwt_extended.utils import get_jwt_header

from app.exc import DuplicatedDataError, InvalidImageError
from app.exc.user_error import InvalidPermissionError
from app.models.episode_model import EpisodeModel
from app.models.watched_episode_model import WatchedEpisodeModel
from app.services import episode_service as Episode
from app.services.helpers import encode_json, paginate
from flask import current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
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
    except BadRequestKeyError:
        return {'message': 'Invalid or missing key name. Required options: anime, episodeNumber, image, videoUrl.'}, HTTPStatus.BAD_REQUEST

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
