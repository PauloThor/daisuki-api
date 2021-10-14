from werkzeug.datastructures import ImmutableMultiDict
from app.models.anime_model import AnimeModel
from app.models.genre_model import GenreModel
from app.models.genre_anime_model import GenreAnimeModel
from app.services.imgur_service import upload_image
from app.services.helpers import verify_admin_mod
from datetime import datetime


def create_anime(files: ImmutableMultiDict, form: ImmutableMultiDict) -> AnimeModel:
    verify_admin_mod()
    image_url  = upload_image(files['image'])

    new_anime = AnimeModel(name=form['name'], synopsis=form['synopsis'])
    new_anime.total_episodes = int(form['totalEpisodes'])
    new_anime.is_movie = bool(form['isMovie'])
    new_anime.is_dubbed = bool(form['isDubbed'])
    new_anime.image_url = image_url
    new_anime.is_completed = False
    new_anime.created_at = datetime.utcnow()

    return new_anime


def set_anime_genres(genres: list, anime: AnimeModel, session) -> AnimeModel:
    for genre in genres:
        genre = genre.strip()
        db_genre = GenreModel.query.filter(GenreModel.name.ilike(genre)).first()
        if not db_genre:
            db_genre = GenreModel(name=genre)
            session.add(db_genre)
            session.commit()
        anime.genres.append(db_genre)
    session.commit()

    return anime
