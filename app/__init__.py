import datetime
from os import getenv

from flask import Flask

from app.configs import commands, cors, database, jwt, migration
from app.routes import api_blueprint


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    app.config['JWT_SECRET_KEY'] = getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=8)

    cors.init_app(app)
    database.init_app(app)
    migration.init_app(app)
    jwt.init_app(app)
    app.register_blueprint(api_blueprint.bp)
    commands.init_app(app)

    return app
