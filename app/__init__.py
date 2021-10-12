from flask import Flask
from app.configs import database, migration, env_configs, jwt, cors, commands
from app.routes import api_blueprint

def create_app():

    app = Flask(__name__)
    env_configs.init_app(app)
    cors.init_app(app)
    database.init_app(app)
    migration.init_app(app)
    jwt.init_app(app)
    app.register_blueprint(api_blueprint.bp)
    commands.init_app(app)

    return app

    