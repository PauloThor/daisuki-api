from sqlalchemy.sql.sqltypes import Boolean
from app.models.episode_model import EpisodeModel
from app.models.anime_model import AnimeModel
from app.services.helpers import verify_admin_mod
from app.services.imgur_service import upload_image
from app.exc import DuplicatedDataError
from datetime import datetime
from sqlalchemy import desc
from werkzeug.datastructures import ImmutableMultiDict

def upload_episode(files: ImmutableMultiDict, form: ImmutableMultiDict, session) -> EpisodeModel:
    verify_admin_mod()

    image_url  = upload_image(files['image'])
    anime = AnimeModel.query.filter_by(name=form['anime']).first()

    check_anime_completed(anime.name, form['episodeNumber'], session)

    if verify_episode_exists(int(form['episodeNumber'])):
        raise DuplicatedDataError('Episode')

    new_episode = EpisodeModel (episode_number=int(form['episodeNumber']))
    new_episode.anime_id = int(anime.id)
    new_episode.image_url = image_url
    new_episode.video_url = form['videoUrl']
    new_episode.created_at = datetime.utcnow()

    return new_episode


def check_anime_completed(anime_name: str, episode_number: int, session) -> None:
    anime = AnimeModel.query.filter_by(name=anime_name).one()

    if anime.total_episodes == episode_number:

        setattr(anime, 'is_completed', True)

        session.add(anime)
        session.commit()


def list_episodes() -> list[EpisodeModel]:
    return EpisodeModel.query.order_by(desc(EpisodeModel.created_at)).all()


def verify_episode_exists(episode_number: int) -> Boolean:
    for episode in list_episodes():
        if episode.episode_number == episode_number:
            return True
    return False