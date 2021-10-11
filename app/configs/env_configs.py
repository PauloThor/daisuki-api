from flask import Flask
from environs import Env

env = Env()
env.read_env()

def init_app(app: Flask):
    
    app.config['SQLALCHEMY_DATABASE_URI'] = env('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = bool(env('SQLALCHEMY_TRACK_MODIFICATIONS'))
    app.config['JSON_SORT_KEYS'] = bool(env('JSON_SORT_KEYS'))
    app.config["JWT_SECRET_KEY"] = env('JWT_SECRET_KEY')
