from dataclasses import asdict
from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_
from http import HTTPStatus
from sqlalchemy.sql.functions import func
from http import HTTPStatus

import psycopg2
import sqlalchemy
import werkzeug
from app.exc import InvalidImageError
from app.exc import user_error as UserErrors
from app.exc.anime_errors import InvalidRating
from app.exc.user_error import InvalidPermissionError
from app.models.anime_model import AnimeModel
from app.models.user_model import UserModel
from app.models.anime_rating_model import AnimeRatingModel
from app.services import anime_service as Animes
from app.services import user_service as Users
from app.exc.user_error import InvalidPermissionError
from app.exc import InvalidImageError
from app.exc import user_error as UserErrors
from functools import reduce
import werkzeug
import sqlalchemy
import psycopg2
from app.services.helpers import decode_json, encode_json, encode_list_json
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
        Users.verify_admin()

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
        Users.verify_admin()

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
        Users.verify_admin()

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
def set_rating(id: int):
    try:
        data = request.json
        if not data['rating'] in [1,2,3,4,5]:
            raise InvalidRating

        current_user = get_jwt_identity()
        user : UserModel = UserModel.query.get(current_user['id'])
        anime : AnimeModel = AnimeModel.query.get(id)
        if not anime:
            return {'message': 'Anime not found'}, HTTPStatus.NOT_FOUND

        session = current_app.db.session

        if anime in user.ratings:
            AnimeRatingModel.query.filter(AnimeRatingModel.anime_id == anime.id, AnimeRatingModel.user_id == user.id).update(data)
            session.commit()
            return '', HTTPStatus.OK

        rating = AnimeRatingModel(rating=data['rating'], user_id=user.id, anime_id=anime.id)
        session.add(rating)
        session.commit()
        return encode_json(rating), HTTPStatus.CREATED
    except sqlalchemy.exc.DataError:
        return {'Invalid Key': {'rating':data['rating']}}, HTTPStatus.BAD_REQUEST
    except InvalidRating:
        return {'msg': 'The rating must be from 1 to 5'}, HTTPStatus.BAD_REQUEST



def get_anime_by_name(anime_name: str):
    try:
        anime_name = anime_name.replace('-',' ')
       
        print(anime_name)
        if "dublado" in anime_name.lower():
            anime_name = anime_name.replace('dublado', '(dublado)')
           
        anime = AnimeModel.query.filter(func.lower(AnimeModel.name)==func.lower(anime_name)).first_or_404()
    
        # print(anime)
        ratings = AnimeRatingModel.query.filter_by(anime_id=anime.id).all()
        
        if ratings:
            ratings = [r.rating for r in ratings]
            rating = reduce((lambda a, b: a + b), ratings) / len(ratings)
            anime = asdict(anime)
            anime['rating'] = round(rating, 2)
        else:
            anime = asdict(anime)
            anime['rating'] = None
       
        return anime, HTTPStatus.OK
    except werkzeug.exceptions.NotFound:
        return {'msg': 'Anime not found'}, HTTPStatus.NOT_FOUND


