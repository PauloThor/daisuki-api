from app.exc.comment_error import CommentError
from app.exc.user_error import InvalidPermissionError
from app.models.anime_model import AnimeModel
from app.models.comment_model import CommentModel
from app.models.episode_model import EpisodeModel
from app.services.helpers import verify_admin_mod
from app.services.imgur_service import upload_image
from app.exc import DataNotFound, DuplicatedDataError
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.sql.sqltypes import Boolean
from werkzeug.datastructures import ImmutableMultiDict

def upload_episode(files: ImmutableMultiDict, form: ImmutableMultiDict, session) -> EpisodeModel:
    verify_admin_mod()

    image_url = upload_image(files['image'])
    anime = AnimeModel.query.filter_by(name=form['anime']).first()

    check_anime_completed(anime.name, form['episodeNumber'], session)

    if verify_episode_exists(int(form['episodeNumber']), int(anime.id)):
        raise DuplicatedDataError('Episode')

    new_episode = EpisodeModel (episode_number=int(form['episodeNumber']))
    new_episode.anime_id = int(anime.id)
    new_episode.image_url = image_url
    new_episode.video_url = form['videoUrl']
    new_episode.created_at = datetime.utcnow()

    return new_episode


def check_anime_completed(anime_name: str, episode_number: int, session) -> None:
    anime = AnimeModel.query.filter_by(name=anime_name).first()

    if not anime:
        raise DataNotFound(f'Anime {anime_name}')

    if anime.total_episodes == episode_number:

        setattr(anime, 'is_completed', True)

        session.add(anime)
        session.commit()


def list_episodes() -> list[EpisodeModel]:
    return EpisodeModel.query.order_by(desc(EpisodeModel.created_at)).all()


def verify_episode_exists(episode_number: int, anime_id: int) -> Boolean:
    for episode in list_episodes():
        if episode.episode_number == episode_number and episode.anime_id == anime_id:
            return True
    return False


def get_episode_by_id(id: int) -> EpisodeModel:
    episode = EpisodeModel.query.get(id)

    if not episode:
        raise DataNotFound('Episode')
    
    return episode


def create_comment_episode(user_id: int, episode_id: int, data: dict) -> CommentModel:

    if len(data['content']) == 0:
        raise CommentError()

    comment = CommentModel(user_id=user_id, episode_id=episode_id)
    comment.content = data['content'] 
    comment.created_at = datetime.utcnow()

    return comment


def delete_comment_episode(user, comment, session):
    if not comment:
        raise DataNotFound('Comment')

    if user['permission'] == 'admin' or user['permission'] == 'mod' or user['id'] == comment.user_id:

        session.delete(comment)
        session.commit()
    else:
        raise InvalidPermissionError