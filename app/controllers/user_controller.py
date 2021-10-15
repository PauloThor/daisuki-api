import datetime
from http import HTTPStatus

import psycopg2
import sqlalchemy
from app.exc import PageNotFoundError, user_error as UserErrors
from app.models.anime_model import AnimeModel
from app.models.user_model import UserModel
from app.services import user_service as Users
from app.services.helpers import decode_json, encode_json, encode_list_json, paginate
from app.services.imgur_service import upload_image
from app.services.helpers import paginate
from flask import current_app, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity,jwt_required


def create():
    try:
        new_user = Users.create_user(request.json)

        session = current_app.db.session

        session.add(new_user)
        session.commit()

        return encode_json(new_user), HTTPStatus.CREATED
    except TypeError as e:
        return {'message': str(e)}, HTTPStatus.BAD_REQUEST

    except sqlalchemy.exc.IntegrityError as e:
    
        if type(e.orig) == psycopg2.errors.NotNullViolation:
            return {'message': str(e.orig).split('\n')[0]}, HTTPStatus.BAD_REQUEST
        
        if type(e.orig) == psycopg2.errors.UniqueViolation:
            return {'message': 'Email already registered'}, HTTPStatus.BAD_REQUEST

    except UserErrors.InvalidUsernameError:
         return {'message': 'Username already exists'}, HTTPStatus.BAD_REQUEST


def get_user(id: int):      
    found_user = UserModel.query.get(id)
    if not found_user:
        return {'message': 'User not found'}, HTTPStatus.NOT_FOUND
    return jsonify({
        'username': found_user.username,
        'avatarUrl': found_user.avatar_url
    })


@jwt_required()
def get_users():
    return encode_list_json(UserModel.query.all()), HTTPStatus.OK


def login():
    data = request.json
    try:
        found_user: UserModel = UserModel.query.filter_by(email=data['email']).one()
        found_user.verify_password(data['password'])

        expires_delta = datetime.timedelta(days=30) if data.get('remindMe') else None

        access_token = create_access_token(identity=found_user, expires_delta=expires_delta)

        return {'accessToken': access_token}, HTTPStatus.OK

    except (sqlalchemy.exc.NoResultFound, UserErrors.InvalidPasswordError):
        return {'message': 'Incorrect email or password'}, HTTPStatus.BAD_REQUEST
    except KeyError as e:
        return {'message': f'{str(e)} is missing'}


@jwt_required()
def update():
    data = decode_json(request.json)
    try:
        found_user = get_jwt_identity()
        if 'password' in data:
            data.pop('password')
        if 'created_at' in data:
            data.pop('created_at')
        if 'permission' in data:
            data.pop('permission')

        UserModel.query.filter_by(id=found_user['id']).update(data)
        
        current_app.db.session.commit() 

        output = UserModel.query.get(found_user['id'])

        return encode_json(output), HTTPStatus.OK
    except sqlalchemy.exc.InvalidRequestError as e:
        return {'message': e.args[0].split('\"')[-2] + ' is invalid'}, HTTPStatus.BAD_REQUEST


@jwt_required()
def update_password():
    data = request.json
    try:
        found_user = UserModel.query.get(get_jwt_identity()['id'])
        found_user.verify_password(data['password'])
        found_user.password = data['newPassword']

        session = current_app.db.session

        session.add(found_user)
        session.commit()

        return {'message': 'Password updated'}, HTTPStatus.OK
    except sqlalchemy.exc.InvalidRequestError as e:
        return {'message': e.args[0].split('\"')[-2] + ' is invalid'}, HTTPStatus.BAD_REQUEST
    
    except (sqlalchemy.exc.NoResultFound, UserErrors.InvalidPasswordError):
        return {'message': 'Incorrect password'}, HTTPStatus.BAD_REQUEST
    
    except KeyError as e:
        return {'message': f'{str(e.args[0])} is missing'}


@jwt_required()
def delete_self():
    found_user = get_jwt_identity()

    user_to_delete: UserModel = UserModel.query.get(found_user['id'])

    session = current_app.db.session
    session.delete(user_to_delete)
    session.commit()

    return jsonify(user_to_delete), HTTPStatus.OK


@jwt_required()
def delete(id: int):
    try:
        Users.verify_admin()

        user_to_delete: UserModel = UserModel.query.get(id)

        session = current_app.db.session
        session.delete(user_to_delete)
        session.commit()

        return jsonify(user_to_delete), HTTPStatus.OK        
    except UserErrors.InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED

    except sqlalchemy.exc.NoResultFound:
        return {'message': 'User not found'}, HTTPStatus.NOT_FOUND


@jwt_required()
def promote():
    data = request.json
    try:
        Users.verify_admin()

        UserModel.query.filter_by(email=data['email']).one()
        UserModel.query.filter_by(email=data['email']).update({'permission': 'mod'})

        current_app.db.session.commit() 

        return '', HTTPStatus.NO_CONTENT
    except UserErrors.InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED
    except sqlalchemy.exc.NoResultFound:
        return {'message': 'User not found'}, HTTPStatus.NOT_FOUND


@jwt_required()
def demote():
    data = request.json
    try:
        Users.verify_admin()

        UserModel.query.filter_by(email=data['email']).one()
        UserModel.query.filter_by(email=data['email']).update({'permission': 'user'})

        current_app.db.session.commit() 

        return '', HTTPStatus.NO_CONTENT
    except UserErrors.InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED
    except sqlalchemy.exc.NoResultFound:
        return {'message': 'User not found'}, HTTPStatus.NOT_FOUND


@jwt_required()
def get_mods():
    all_users = UserModel.query.all()

    output = [user for user in all_users if user.permission == 'mod']

    return encode_list_json(output)


@jwt_required()
def post_favorite(anime_id: int):
    found_user = get_jwt_identity()

    try:
        anime = AnimeModel.query.get(anime_id)
        user = UserModel.query.get(found_user['id'])

        if anime in user.favorites:
            raise UserErrors.InvalidFavoriteError

        user.favorites.append(anime)

        session = current_app.db.session
        session.commit() 

        return '', HTTPStatus.NO_CONTENT
    except UserErrors.InvalidFavoriteError:
        return {'message': f'User has already favorited {anime.name}'}, HTTPStatus.BAD_REQUEST


@jwt_required()
def get_favorites():
    try:
        found_user = get_jwt_identity()
        query = UserModel.query.get(found_user['id'])

        output = paginate(query.favorites)

        return jsonify(output), HTTPStatus.OK
    except ValueError:
        return {'message': 'Arguments should be integers'}, HTTPStatus.BAD_REQUEST
    except PageNotFoundError as e:
        return e.message, HTTPStatus.BAD_REQUEST


@jwt_required()
def delete_favorite(anime_id: int):
    try:
        found_user = get_jwt_identity()

        anime = AnimeModel.query.get(anime_id)
        user = UserModel.query.get(found_user['id'])

        index = user.favorites.index(anime)
        user.favorites.pop(index)

        session = current_app.db.session
        session.commit() 

        return '', HTTPStatus.NO_CONTENT
    except ValueError:
        return {'message': f'The user did not favorite {anime.name}'}, HTTPStatus.BAD_REQUEST


@jwt_required()
def update_avatar():
    found_user = get_jwt_identity()
    image_url  = upload_image(request.files['image'])
    
    UserModel.query.filter_by(id=found_user['id']).update({'avatar_url': image_url})

    session = current_app.db.session
    session.commit()

    return {'avatarUrl': image_url}, HTTPStatus.OK
 

@jwt_required()
def get_watched():
    found_user = get_jwt_identity()
    try:
        user = UserModel.query.get(found_user['id'])

        output = paginate(user.watched)

        return jsonify(output)
    except PageNotFoundError as e:
        return e.message, HTTPStatus.BAD_REQUEST


