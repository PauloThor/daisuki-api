from flask import Flask, current_app
from flask.cli import AppGroup
from app.models.genre_model import GenreModel
from app.models.anime_model import AnimeModel
from app.models.genre_anime_model import GenreAnimeModel
from app.models.episode_model import EpisodeModel
from json import load


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


def init_app(app: Flask):
    cli_genres(app)
    cli_animes(app)
    cli_episodes(app)
