from app.models.episode_model import EpisodeModel
from app.exc import InvalidImageError, DuplicatedDataError
from app.exc.UserErrors import InvalidPermissionError
from app.services import episode_service as Episode
from app.services.helpers import paginate
from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from http import HTTPStatus
from werkzeug.exceptions import BadRequestKeyError

@jwt_required()
def create_episode():
    data = request.form
    session = current_app.db.session

    try:
        new_episode = Episode.upload_episode(request.files, data, session)
        session.add(new_episode)
        session.commit()

        return jsonify(new_episode), HTTPStatus.CREATED
    except InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED
    except InvalidImageError as e:
        return e.message, HTTPStatus.BAD_REQUEST
    except DuplicatedDataError as e:
        return e.message, HTTPStatus.BAD_REQUEST
    except BadRequestKeyError:
        return {'message': 'Invalid or missing key name. Required options: anime, episode_number, image, video_url.'}, HTTPStatus.BAD_REQUEST

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