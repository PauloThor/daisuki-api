from flask import request, jsonify, current_app
from http import HTTPStatus
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import sqlalchemy
from app.exc.UserErrors import InvalidPasswordError, InvalidPermissionError
import psycopg2


from app.models.user_model import UserModel
from app.services import user_service as Users


def create():
    try:
        new_user = Users.create_user(request.json)

        session = current_app.db.session

        session.add(new_user)
        session.commit()

        return jsonify(new_user), HTTPStatus.CREATED
    except TypeError as e:
        return {'msg': str(e)}, HTTPStatus.BAD_REQUEST

    except sqlalchemy.exc.IntegrityError as e:
    
        if type(e.orig) == psycopg2.errors.NotNullViolation:
            return {'msg': str(e.orig).split('\n')[0]}, HTTPStatus.BAD_REQUEST
        
        if type(e.orig) == psycopg2.errors.UniqueViolation:
            return {'msg': 'User already exists'}, HTTPStatus.BAD_REQUEST


@jwt_required()
def get_user(id: int):
    try:        
        found_user = UserModel.query.get(id)
        if found_user == None:
            return jsonify([])
        return jsonify(found_user)
    except (sqlalchemy.exc.NoResultFound, InvalidPasswordError):
        return {'msg': 'User not found'}, HTTPStatus.BAD_REQUEST


@jwt_required()
def get_users():
    return jsonify(UserModel.query.all()), HTTPStatus.OK


def login():
    data = request.json
    try:
        found_user: UserModel = UserModel.query.filter_by(email=data['email']).one()
        found_user.verify_password(data['password'])

        access_token = create_access_token(identity=found_user)

        return {'access_token': access_token}, HTTPStatus.OK

    except (sqlalchemy.exc.NoResultFound, InvalidPasswordError):
        return {'msg': 'Incorrect email or password'}, HTTPStatus.BAD_REQUEST


@jwt_required()
def update():
    data = request.json
    try:
        found_user = get_jwt_identity()
        data.pop('password')
        UserModel.query.filter_by(id=found_user['id']).update(data)
        
        session = current_app.db.session
        session.commit() 

        output = UserModel.query.get(found_user['id'])

        return jsonify(output), HTTPStatus.OK
    except sqlalchemy.exc.InvalidRequestError as e:
        return {'msg': e.args[0].split('\"')[-2] + ' is invalid'}, HTTPStatus.BAD_REQUEST


@jwt_required()
def delete_self():
    found_user = get_jwt_identity()

    user_to_delete: UserModel = UserModel.query.get(found_user['id'])

    session = current_app.db.session
    session.delete(user_to_delete)
    session.commit()

    return {"msg": "User deleted"}, HTTPStatus.OK


@jwt_required()
def delete(id: int):
    try:
        Users.verify_admin()

        user_to_delete: UserModel = UserModel.query.get(id)

        session = current_app.db.session
        session.delete(user_to_delete)
        session.commit()

        return {"msg": "User deleted"}, HTTPStatus.OK        
    except InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED

    except sqlalchemy.exc.NoResultFound:
        return {'msg': 'User not found'}, HTTPStatus.BAD_REQUEST


@jwt_required()
def promote():
    data = request.json
    try:
        Users.verify_admin()

        UserModel.query.filter_by(email=data['email']).update({'permission': 'mod'})

        session = current_app.db.session
        session.commit() 

        return '', HTTPStatus.OK
    except InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED


@jwt_required()
def demote():
    data = request.json
    try:
        Users.verify_admin()

        UserModel.query.filter_by(email=data['email']).update({'permission': 'user'})

        session = current_app.db.session
        session.commit() 

        return '', HTTPStatus.OK
    except InvalidPermissionError as e:
        return e.message, HTTPStatus.UNAUTHORIZED


@jwt_required()
def get_mods():
    all_users = UserModel.query.all()

    output = [user for user in all_users if user.permission == 'mod']

    return jsonify(output)