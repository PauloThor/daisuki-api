from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_
from http import HTTPStatus
from sqlalchemy.sql.functions import func
from app.exc.anime_errors import InvalidRating
from app.models.anime_model import AnimeModel
from app.models.anime_rating_model import AnimeRatingModel
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
    except sqlalchemy.exc.InvalidRequestError as e:
        return {'msg': e.args[0].split('\"')[-2] + ' is invalid'}, HTTPStatus.BAD_REQUEST



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



@jwt_required()
def create_or_update_rating(id: int):
    try:
        data = request.json

        if not data['rating'] in [1,2,3,4,5]:
            raise InvalidRating

        user = get_jwt_identity()
        data['user_id'] = user['id']
        data['anime_id'] = id

        query = AnimeRatingModel.query.filter(
        and_(
            AnimeRatingModel.user_id == user['id'],
            AnimeRatingModel.anime_id == id
        )
        ).first()

        session = current_app.db.session

        if(query):
            for key, value in data.items():
                    setattr(query, key, value)

            session.add(query)
            session.commit()

            return jsonify(query), HTTPStatus.OK
        else:
            rating = AnimeRatingModel(**data)

            session.add(rating)
            session.commit()

            return jsonify(rating), HTTPStatus.CREATED

    except TypeError:
        return {'msg': 'invalid key'}, HTTPStatus.BAD_REQUEST
    except sqlalchemy.exc.DataError:
        return {'Invalid Key': {'rating':data['rating']}}, HTTPStatus.BAD_REQUEST
    except werkzeug.exceptions.BadRequest:
        return {'msg': "The request needs a JSON with the 'rating' field containing a number from 1 to 5"}, HTTPStatus.BAD_REQUEST
    except InvalidRating:
        return {'msg': 'The rating must be from 1 to 5'}, HTTPStatus.BAD_REQUEST



def get_anime_by_name(anime_name: str):
    try:
        anime_name = anime_name.replace('-',' ')
        if "dublado" in anime_name.lower():
            anime_name = anime_name.replace('dublado', '(dublado)')
           
        anime = AnimeModel.query.filter(func.lower(AnimeModel.name)==func.lower(anime_name)).first_or_404()
       
        return jsonify(anime), HTTPStatus.OK
    except werkzeug.exceptions.NotFound:
        return {'msg': 'Anime not found'}, HTTPStatus.NOT_FOUND


