from http import HTTPStatus

from app.exc import DuplicatedDataError, InvalidImageError, PageNotFoundError, DataNotFound
from app.exc.comment_error import CommentError
from app.exc.user_error import InvalidPermissionError
from app.models.comment_model import CommentModel
from app.models.episode_model import EpisodeModel
from app.models.watched_episode_model import WatchedEpisodeModel
from app.services import episode_service as Episode
from app.services.helpers import encode_json, decode_json, paginate, verify_admin_mod
from app.services.imgur_service import upload_image
from flask import current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, asc
from sqlalchemy.exc import InvalidRequestError, IntegrityError
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


@jwt_required(optional=True)
def watch_episode(id: int):
    found_user = get_jwt_identity()
    try:
        episode = EpisodeModel.query.get(id)

        episode.views += 1
        today = datetime.utcnow()
        session = current_app.db.session

        if found_user:
            watched = WatchedEpisodeModel(user_id=found_user['id'], episode_id=id, watched_at=today)

            session.add(watched)
        
        session.commit()

        return '', HTTPStatus.NO_CONTENT
    except AttributeError:
        return {'msg': 'Episode not found'}, HTTPStatus.BAD_REQUEST


@jwt_required()
def create_comment(id: int):
    try:
        user = get_jwt_identity()
        data = decode_json(request.json)

        comment = Episode.create_comment_episode(user['id'], id, data)
        session = current_app.db.session

        session.add(comment)
        session.commit()

        return encode_json(comment), HTTPStatus.CREATED
    except CommentError as e:
        return e.message, HTTPStatus.BAD_REQUEST
    except IntegrityError:
        return {'message': 'Episode not found.'}, HTTPStatus.NOT_FOUND
    except KeyError:
        return {'message': 'Invalid or missing key name. Required option: content.'}, HTTPStatus.BAD_REQUEST

def get_comments(id: int):
    order_comment = request.args.get('order_by', False)

    if order_comment:
        list_comments = CommentModel.query.filter_by(episode_id=id).order_by(asc(CommentModel.created_at)).all()
    else:
        list_comments = CommentModel.query.filter_by(episode_id=id).order_by(desc(CommentModel.created_at)).all()

    return paginate(list_comments, 10), HTTPStatus.OK


@jwt_required()
def delete_comment(id: int, comment_id:int):
    user = get_jwt_identity()
    comment = CommentModel.query.get(comment_id)
    session = current_app.db.session

    try:
        Episode.delete_comment_episode(user, comment, session)
        return '', HTTPStatus.NO_CONTENT
    except DataNotFound as e:
        return e.message, HTTPStatus.NOT_FOUND
    except InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED
    
