from http import HTTPStatus

import psycopg2
import sqlalchemy
import werkzeug
from app.exc import InvalidImageError
from app.exc import user_error as UserErrors
from app.exc.anime_errors import InvalidRating
from app.exc.user_error import InvalidPermissionError
from app.models.anime_model import AnimeModel
from app.models.anime_rating_model import AnimeRatingModel
from app.services import anime_service as Animes
from app.services.helpers import decode_json, encode_json, encode_list_json, verify_admin_mod
from app.services.imgur_service import upload_image
from flask import current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity


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
        return encode_json(anime), HTTPStatus.CREATED
    except InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED
    except InvalidImageError as e:
        return e.message, HTTPStatus.BAD_REQUEST
    except werkzeug.exceptions.BadRequestKeyError as e:
        return {'message': 'Invalid or missing key name. Required options: name, synopsis, image, totalEpisodes, isMovie, isDubbed, genres.'}, HTTPStatus.BAD_REQUEST
    except sqlalchemy.exc.IntegrityError as e:
        if type(e.orig) == psycopg2.errors.UniqueViolation:
            return {'message': 'Anime already registered!'}, HTTPStatus.CONFLICT


@jwt_required()
def update(id: int):
    try:
        verify_admin_mod()

        data = decode_json(request.json)

        AnimeModel.query.filter_by(id=id).update(data)

        current_app.db.session.commit()

        anime = AnimeModel.query.get(id)
        if not anime:
            return {'message': 'Anime not found'}, HTTPStatus.NOT_FOUND

        return encode_json(anime), HTTPStatus.OK
    except UserErrors.InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED
    except sqlalchemy.exc.InvalidRequestError as e:
        return {'message': e.args[0].split('\"')[-2] + ' is invalid'}, HTTPStatus.BAD_REQUEST



@jwt_required()
def update_avatar(id: int):
    try:
        verify_admin_mod()

        AnimeModel.query.filter_by(id=id).one()

        image_url  = upload_image(request.files['image'])
        
        AnimeModel.query.filter_by(id=id).update({'image_url': image_url})

        current_app.db.session.commit()

        return {'imageUrl': image_url}, HTTPStatus.OK
    except UserErrors.InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED
    except werkzeug.exceptions.BadRequestKeyError as e:
        return {'message': 'Missing form field image.'}, HTTPStatus.BAD_REQUEST
    except sqlalchemy.exc.NoResultFound:
        return {'message': 'Anime not found'}, HTTPStatus.NOT_FOUND


def get_animes():
    return encode_list_json(AnimeModel.query.all())


@jwt_required()
def delete(id: int):
    try:
        verify_admin_mod()

        anime_to_delete: AnimeModel = AnimeModel.query.get(id)

        if not anime_to_delete:
            return {'message': 'Anime not found'}, HTTPStatus.NOT_FOUND

        session = current_app.db.session
        session.delete(anime_to_delete)
        session.commit()
        return {'message': 'Anime deleted'}, HTTPStatus.OK        
    except UserErrors.InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED


@jwt_required()
def create_or_update_rating(id: int):
    try:
        data = request.json

        if not data['rating'] in [1,2,3,4,5]:
            raise InvalidRating

        user = get_jwt_identity()

        query = AnimeRatingModel.query.filter(AnimeRatingModel.user_id == user['id'],AnimeRatingModel.anime_id == id).first()

        session = current_app.db.session

        if(query):
            for key, value in data.items():
                    setattr(query, key, value)

            session.add(query)
            session.commit()

            return encode_json(query), HTTPStatus.OK
        else:
            rating = AnimeRatingModel(**data)

            session.add(rating)
            session.commit()

            return encode_json(rating), HTTPStatus.CREATED

    except TypeError:
        return {'message': 'Invalid key'}, HTTPStatus.BAD_REQUEST
    except sqlalchemy.exc.DataError:
        return {'Invalid Key': {'rating':data['rating']}}, HTTPStatus.BAD_REQUEST
    except werkzeug.exceptions.BadRequest:
        return {'message': 'The request needs a JSON with the "rating" field containing a number from 1 to 5'}, HTTPStatus.BAD_REQUEST
    except InvalidRating:
        return {'message': 'The rating must be from 1 to 5'}, HTTPStatus.BAD_REQUEST
