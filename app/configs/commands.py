from flask import Flask, current_app
from flask.cli import AppGroup
from click import argument, option, echo
from app.models.genre_model import GenreModel
from app.models.anime_model import AnimeModel
from app.models.genre_anime_model import GenreAnimeModel
from app.models.episode_model import EpisodeModel
from json import load
from datetime import datetime

from app.models.user_model import UserModel


def read_json(filename: str):
    with open(filename) as j_file:
        return load(j_file)


def cli_genres(app: Flask):
    cli = AppGroup('cli_genres')

    @cli.command('create')
    def cli_genres_create():
        session = current_app.db.session
        data = [
            'Ação', 'Aventura', 'Comédia', 'Drama', 'Esporte', 'Fantasia', 'Ficção científica', 'Gourmet', 'Horror',
            'Josei', 'Mecha', 'Mistério', 'Romance', 'Seinen', 'Slice of life', 'Sobrenatural', 'Suspense'
        ]

        to_insert = [GenreModel(name=genre) for genre in data]

        session.add_all(to_insert)
        session.commit()
    
    app.cli.add_command(cli)


def cli_animes(app: Flask):
    cli = AppGroup('cli_animes')

    @cli.command('create')
    def cli_animes_create():
        session = current_app.db.session
        data = read_json('snippet_animes.json')

        to_insert = [AnimeModel(**anime) for anime in data]
        
        session.add_all(to_insert)
        session.commit()

        data_genres_animes = read_json('snippet_genres_animes.json')

        to_insert = [GenreAnimeModel(**data) for data in data_genres_animes]
    
        session.add_all(to_insert)
        session.commit()


    app.cli.add_command(cli)


def cli_episodes(app: Flask):
    cli = AppGroup('cli_episodes')

    @cli.command('create')
    def cli_episodes_create():
        session = current_app.db.session
        data = read_json('snippet_episodes.json')

        to_insert = [EpisodeModel(**episode) for episode in data]
        
        session.add_all(to_insert)
        session.commit()

    app.cli.add_command(cli)


def cli_admin(app: Flask):
    cli = AppGroup('cli_admin')
    session = current_app.db.session

    @cli.command('create')
    @argument('email')
    @argument('username')
    @argument('password')
    @option('avatar_url')
    def cli_create_admin(email: str, username: str, password: str):
        admin_check = UserModel.query.filter_by(email=email).first()
        echo(f'email: {email}, username: {username}')
        if admin_check:
            echo('')
            echo(f'Error: user with the email {email} already registered.')
            echo(f'Use the "flask cli_admin upgrade --email={email}" command')
            return None
        
        admin_check = UserModel.query.filter_by(username=username).first()
        if admin_check:
            echo('')
            echo(f'Error: user with the username {username} already registered.')
            echo(f'Use the "flask cli_admin upgrade --username={username}" command')
            return None


        new_admin = UserModel(email=email, username=username)
        new_admin.permission = 'admin'
        new_admin.created_at = datetime.utcnow()
        new_admin.updated_at = datetime.utcnow()
        new_admin.password = password

        session.add(new_admin)
        session.commit()
        echo('Admin successfully created.')

    @cli.command('upgrade')
    @option('--email', default=None)
    @option('--username', default=None)
    def cli_admin_upgrade(email: str, username: str):
        if email:
            user_to_admin = UserModel.query.filter_by(email=email).first()
            
            if not user_to_admin:
                echo(f'Error: the email {email} is not registered.')
                return None

            setattr(user_to_admin, 'permission', 'admin')
            session.add(user_to_admin)
            session.commit()
            echo('User updated successfully.')

        if username:
            user_to_admin = UserModel.query.filter_by(username=username).first()
            
            if not user_to_admin:
                echo(f'Error: the username {username} is not registered.')
                return None

            setattr(user_to_admin, 'permission', 'admin')
            session.add(user_to_admin)
            session.commit()
            echo('User updated successfully.')

    @cli.command('downgrade')
    @argument('email')
    @option('permission')
    def cli_admin_downgrade(email: str, permission: str = 'user'):
        user_to_admin = UserModel.query.filter_by(email=email).first()
            
        if not user_to_admin:
            echo(f'Error: the email {email} is not registered.')
            return None

        setattr(user_to_admin, 'permission', permission)
        session.add(user_to_admin)
        session.commit()
        echo('User demoted successfully.')

    app.cli.add_command(cli)

def init_app(app: Flask):
    cli_genres(app)
    cli_animes(app)
    cli_episodes(app)
    cli_admin(app)
