from flask import request, jsonify, current_app
from http import HTTPStatus
from flask_jwt_extended import create_access_token, jwt_required
from flask_httpauth import HTTPAuth, HTTPTokenAuth

from app.models.user_model import UserModel

auth = HTTPTokenAuth(scheme='Bearer')

def create():
    data = request.json

    password_to_hash = data.pop('password')

    new_user = UserModel(**data)
    new_user.password = password_to_hash

    session = current_app.db.session

    session.add(new_user)
    session.commit()

    return jsonify(new_user), HTTPStatus.CREATED


def login():
    data = request.json

    found_user: UserModel = UserModel.query.filter_by(email=data['email']).first()

    if not found_user:
        return {"message": "User not found"}, HTTPStatus.NOT_FOUND
    
    if not found_user.verify_password(data['password']):
        return {'message': 'Unauthorized'}, HTTPStatus.UNAUTHORIZED
    
    access_token = create_access_token(identity=found_user)
    return {'access_token': access_token}, HTTPStatus.OK


@jwt_required()
def update():

    data = request.json

    # TODO MUDAR PRA PEGAR O USER PELO TOKEN

    found_user: UserModel = UserModel.query.filter_by(email=data['email']).first()

    if not found_user:
        return {"message": "User not found"}, HTTPStatus.NOT_FOUND
    
    if not found_user.verify_password(data['password']):
        return {'message': 'Unauthorized'}, HTTPStatus.UNAUTHORIZED

    data.pop('password')

    UserModel.query.filter_by(email=data['email']).update(data)
    
    session = current_app.db.session
    session.commit() 

    output = UserModel.query.get(found_user.id)

    return jsonify(output), HTTPStatus.OK