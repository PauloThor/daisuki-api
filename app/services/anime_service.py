from werkzeug.datastructures import ImmutableMultiDict
from app.models.anime_model import AnimeModel
from app.services.imgur_service import upload_image
from datetime import datetime


def create_anime(files: ImmutableMultiDict, form: ImmutableMultiDict) -> AnimeModel:
    image_url  = upload_image(files['image'])

    new_anime = AnimeModel(name=form['name'], synopsis=form['synopsis'])
    new_anime.total_episodes = int(form['total_episodes'])
    new_anime.is_movie = bool(form['is_movie'])
    new_anime.is_dubbed = bool(form['is_dubbed'])
    new_anime.image_url = image_url
    new_anime.is_completed = False
    new_anime.created_at = datetime.utcnow()

    return new_anime
