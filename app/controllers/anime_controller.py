from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required
from http import HTTPStatus
from app.models.anime_model import AnimeModel
from app.services import anime_service as Animes
from app.services.imgur_service import upload_image
from app.services import user_service as Users
from app.exc.user_error import InvalidPermissionError
from app.exc import InvalidImageError
from app.exc import user_error as UserErrors
import werkzeug
import sqlalchemy
import psycopg2


@jwt_required()
def create():
    form_data = request.form
    try:
        new_anime = Animes.create_anime(request.files, form_data)
        session = current_app.db.session
        session.add(new_anime)
        session.commit()
        genres = form_data['genres'].split(',')
        anime = Animes.set_anime_genres(genres, new_anime, session)
        return jsonify(anime), HTTPStatus.CREATED
    except InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED
    except InvalidImageError as e:
        return e.message, HTTPStatus.BAD_REQUEST
    except werkzeug.exceptions.BadRequestKeyError as e:
        return {'message': 'Invalid or missing key name. Required options: name, synopsis, image, total_episodes, is_movie, is_dubbed, genres.'}, HTTPStatus.BAD_REQUEST
    except sqlalchemy.exc.IntegrityError as e:
        if type(e.orig) == psycopg2.errors.UniqueViolation:
            return {'message': 'Anime already registered!'}, HTTPStatus.CONFLICT


@jwt_required()
def update(id: int):
    try:
        Users.verify_admin()

        data = request.json

        AnimeModel.query.filter_by(id=id).update(data)

        session = current_app.db.session
        session.commit()

        output = AnimeModel.query.get(id)

        return jsonify(output), HTTPStatus.OK
    except UserErrors.InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED


@jwt_required()
def update_avatar(id: int):
    try:
        Users.verify_admin()

        image_url  = upload_image(request.files['image'])
        
        AnimeModel.query.filter_by(id=id).update({'image_url': image_url})

        session = current_app.db.session
        session.commit()

        return {"image_url": image_url}, HTTPStatus.OK
    except UserErrors.InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED


def get_animes():
    return jsonify(AnimeModel.query.all())


@jwt_required()
def delete(id: int):
    try:
        Users.verify_admin()

        anime_to_delete: AnimeModel = AnimeModel.query.get(id)

        session = current_app.db.session
        session.delete(anime_to_delete)
        session.commit()

        return {"msg": "Anime deleted"}, HTTPStatus.OK        
    except UserErrors.InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED

    except sqlalchemy.exc.NoResultFound:
        return {'msg': 'Anime not found'}, HTTPStatus.BAD_REQUEST



