import re
from dataclasses import asdict
from datetime import datetime
from functools import reduce
from http import HTTPStatus

import humps
import psycopg2
import sqlalchemy
import werkzeug
from app.exc import DataNotFound, InvalidImageError, PageNotFoundError
from app.exc import user_error as UserErrors
from app.exc.anime_errors import InvalidRating
from app.exc.user_error import InvalidPermissionError
from app.models.anime_model import AnimeModel
from app.models.anime_rating_model import AnimeRatingModel
from app.models.episode_model import EpisodeModel
from app.models.genre_model import GenreModel
from app.models.user_model import UserModel
from app.services import anime_service as Animes
from app.services import user_service as Users
from app.services.helpers import (decode_json, encode_json, encode_list_json,
                                  paginate, verify_admin_mod)
from app.services.imgur_service import upload_image
from flask import current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import desc, func
from sqlalchemy.sql.functions import func
from unidecode import unidecode


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
        data.update({'updated_at': datetime.utcnow()})

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
        
        AnimeModel.query.filter_by(id=id).update({'image_url': image_url, 'updated_at': datetime.utcnow()})

        current_app.db.session.commit()

        return {'imageUrl': image_url}, HTTPStatus.OK
    except UserErrors.InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED
    except werkzeug.exceptions.BadRequestKeyError as e:
        return {'message': 'Missing form field image.'}, HTTPStatus.BAD_REQUEST
    except sqlalchemy.exc.NoResultFound:
        return {'message': 'Anime not found'}, HTTPStatus.NOT_FOUND


def get_animes():
    try:
        animes = AnimeModel.query
        
        for k in request.args:
            param = request.args.get(k)

            if hasattr(AnimeModel, k):
                animes = animes.filter(getattr(AnimeModel,k)==param)
            if k == 'starts_with':
                    animes = animes.filter(AnimeModel.name.startswith(param.upper()))
        
        animes = paginate(animes.all(), 24)

        for anime in animes['data']:
            ratings = AnimeRatingModel.query.filter_by(anime_id=anime['id']).all()        

            if ratings:
                    ratings = [r.rating for r in ratings]
                    rating = reduce((lambda a, b: a + b), ratings) / len(ratings)
                    anime['rating'] = round(rating, 2) 
            else:
                    anime['rating'] = None

        order_by = request.args.get('order_by')

        if order_by and order_by.lower() =='rating':
            animes_rating_sorted = sorted(animes['data'], reverse=True, key=lambda a: a['rating'] if a['rating'] else 0)
            return jsonify({    
                'page': animes['page'],
                'previous': animes['previous'],
                'next': animes['next'],
                'total': animes['total'],
                'data': animes_rating_sorted
                })
        return jsonify(animes)
    except sqlalchemy.exc.DataError as e:
        return {'message' : 'Invalid query param value'}, HTTPStatus.BAD_REQUEST


def get_genres():
    genres = GenreModel.query.order_by(GenreModel.name).all()
    return jsonify(genres), HTTPStatus.OK


def get_by_genre(genre_name):
    try:
        genre_name = genre_name.title()

        genres = GenreModel.query.all()

        genre = None
        
        for data in genres:
            if unidecode(data.name) == unidecode(genre_name):
                genre = data
                break
                
        if not genre:
            raise DataNotFound('Genre')
        
        animes_by_genre = GenreModel.query.get(genre.id)
        animes = animes_by_genre.animes

        starts_with = request.args.get('starts_with')

        if starts_with:
            animes = [anime for anime in animes if anime.name.startswith(starts_with.upper())]

        animes = paginate(animes, 24)

        for anime in animes['data']:
            ratings = AnimeRatingModel.query.filter_by(anime_id=anime['id']).all()        

            if ratings:
                    ratings = [r.rating for r in ratings]
                    rating = reduce((lambda a, b: a + b), ratings) / len(ratings)
                    anime['rating'] = round(rating, 2) 
            else:
                    anime['rating'] = None
        return jsonify(animes)
    except DataNotFound as e:
        return e.message, HTTPStatus.NOT_FOUND


def get_latest_animes():
    animes = AnimeModel.query.order_by(sqlalchemy.desc(AnimeModel.created_at)).limit(10)

    return encode_list_json(animes)


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
        return encode_json(anime_to_delete), HTTPStatus.OK        
    except UserErrors.InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED


@jwt_required()
def set_rating(id: int):
    try:
        data = request.json
        if len(data) > 1:
            return {'message': 'The request body must contain only the ranting field'}, HTTPStatus.BAD_REQUEST
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
            return '', HTTPStatus.NO_CONTENT

        rating = AnimeRatingModel(rating=data['rating'], user_id=user.id, anime_id=anime.id)
        session.add(rating)
        session.commit()
        return encode_json(rating), HTTPStatus.CREATED
    except sqlalchemy.exc.DataError:
        return {'Invalid Key': {'rating':data['rating']}}, HTTPStatus.BAD_REQUEST
    except InvalidRating:
        return {'message': 'The rating must be from 1 to 5'}, HTTPStatus.BAD_REQUEST
    except sqlalchemy.exc.InvalidRequestError:
        return {'message': 'The request body must contain only the ranting field'}, HTTPStatus.BAD_REQUEST
    except (KeyError):
        return {'message': 'The requisition body must contain the rating field.'}, HTTPStatus.BAD_REQUEST


def get_most_popular():
    rows = current_app.db.session.query(AnimeModel.name, AnimeModel.image_url, func.avg(EpisodeModel.views).label('avg_views'))\
            .join(EpisodeModel, EpisodeModel.anime_id == AnimeModel.id)\
            .group_by(AnimeModel.name, AnimeModel.image_url)\
            .order_by(desc('avg_views'))\
            .limit(10)\
            .all()

    data = [{'name': row[0], 'imageUrl': row[1], 'averageViews': int(row[2])} for row in rows]

    return jsonify(data), HTTPStatus.OK


def search():
    try:
        anime_name = request.json['anime']
        
        query = AnimeModel.query.filter(AnimeModel.name.ilike(f'%{anime_name}%')).all()

        return encode_list_json(query), HTTPStatus.OK    
    except (TypeError, KeyError):
        return {'message': 'There should be a prop named anime with a string value'}


def get_anime_by_name(anime_name: str):
   try:
       anime_name = re.sub('[^a-zA-Z0-9 \n\.]', '', anime_name)
       anime = AnimeModel.query.filter(func.lower(func.regexp_replace(AnimeModel.name, '[^a-zA-Z0-9\n\.]', '','g'))==func.lower(anime_name)).first_or_404()
       ratings = AnimeRatingModel.query.filter_by(anime_id=anime.id).all()
       synopsis = anime.synopsis
       genres = anime.genres
       anime = asdict(anime)
       anime['synopsis'] = synopsis
       anime['genres'] = [genre.name for genre in genres]
 
       if ratings:
           ratings = [r.rating for r in ratings]
           rating = reduce((lambda a, b: a + b), ratings) / len(ratings)
           anime['rating'] = round(rating, 2)
       else:
           anime['rating'] = None

       return jsonify(humps.camelize(anime)), HTTPStatus.OK
   except werkzeug.exceptions.NotFound:
       return {'message': 'Anime not found'}, HTTPStatus.NOT_FOUND


@jwt_required(optional=True)
def get_anime_episodes(anime_name: str):
    try:
        anime_name = re.sub('[^a-zA-Z0-9 \n\.]', '', anime_name)
        anime = AnimeModel.query.filter(func.lower(func.regexp_replace(AnimeModel.name, '[^a-zA-Z0-9\n\.]', '','g'))==func.lower(anime_name)).first_or_404()
        episodes = paginate(anime.episodes, 24)
        current_user = get_jwt_identity()
        
        if current_user:
            user = UserModel.query.filter_by(id=current_user['id']).first()
            watched_episodes = [episode.id for episode in user.watched]
            for episode in episodes['data']:
                if episode['id'] in watched_episodes:
                    episode['hasWatched'] = True
                else:
                    episode['hasWatched'] = False       
            
        return jsonify(episodes), HTTPStatus.OK
    except werkzeug.exceptions.NotFound:
       return {'message': 'Anime not found'}, HTTPStatus.NOT_FOUND
    except PageNotFoundError:
        return {'message': 'Anime not found'}, HTTPStatus.NOT_FOUND
    except ZeroDivisionError:
        return {'message': 'Invalid url'}, HTTPStatus.BAD_REQUEST


def get_anime_episode_by_number(anime_name: str, episode_number: int):
    try:
        anime_name = re.sub('[^a-zA-Z0-9 \n\.]', '', anime_name)
        anime = AnimeModel.query.filter(func.lower(func.regexp_replace(AnimeModel.name, '[^a-zA-Z0-9\n\.]', '','g'))==func.lower(anime_name)).first_or_404()
        all_episodes = sorted(anime.episodes, key=lambda x: x.episode_number)

        episode = paginate(all_episodes, 1, episode_number)
    
        episode['anime'] = humps.camelize(asdict(anime))
         
        return jsonify(episode), HTTPStatus.OK
    except werkzeug.exceptions.NotFound:
       return {'message': 'Anime not found'}, HTTPStatus.NOT_FOUND
    except PageNotFoundError:
        return {'message': 'Episode not found'}, HTTPStatus.NOT_FOUND
    except ZeroDivisionError:
        return {'message': 'Invalid url'}, HTTPStatus.BAD_REQUEST


def get_name_animes_incompleted():
    animes = AnimeModel.query.filter(AnimeModel.is_completed==False).order_by(AnimeModel.name).all()
    output = [anime.name for anime in animes]
    return jsonify(output)
