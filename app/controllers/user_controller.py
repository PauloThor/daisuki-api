from flask import request, jsonify, current_app
from http import HTTPStatus
from flask_jwt_extended import create_access_token, jwt_required, get_current_user

from app.models.user_model import UserModel
from app.services import user_service as Users


def create():
    new_user = Users.create_user(request.json)

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
    return ''
    return jsonify(get_current_user())
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