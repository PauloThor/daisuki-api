import datetime
from os import getenv

from flask import Flask

from app.configs import commands, cors, database, jwt, migration, mail, cache
from app.routes import api_blueprint


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    app.config['JWT_SECRET_KEY'] = getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=8)

    app.config["MAIL_SERVER"] = getenv("MAIL_SERVER")
    app.config["MAIL_PORT"] = getenv("MAIL_PORT")
    app.config["MAIL_USE_TLS"] = False
    app.config["MAIL_USE_SSL"] = True
    app.config["MAIL_USERNAME"] = getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = getenv("MAIL_USERNAME")
    app.config["MAIL_MAX_EMAILS"] = None
    app.config["MAIL_ASCII_ATTACHMENTS"] = False
    
    if getenv('FLASK_ENV') == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL').replace('postgres', 'postgresql')    
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = getenv('SQLALCHEMY_DATABASE_URI')

    cors.init_app(app)
    database.init_app(app)
    migration.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    app.register_blueprint(api_blueprint.bp)
    commands.init_app(app)

    return app
