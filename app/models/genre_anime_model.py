from app.configs.database import db


genres_animes = db.Table('genres_animes',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id')),
    db.Column('anime_id', db.Integer, db.ForeignKey('animes.id'))
)
