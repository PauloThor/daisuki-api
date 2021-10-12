from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus
from app.models.anime_model import AnimeModel
from app.services import anime_service as Animes
from app.exc import InvalidImageError
import werkzeug
import sqlalchemy
import psycopg2


def create():
    try:
        new_anime = Animes.create_anime(request.files, request.form)
        session = current_app.db.session
        session.add(new_anime)
        session.commit(new_anime)
        
        return jsonify(new_anime), HTTPStatus.CREATED
    except InvalidImageError as e:
        return e.message, HTTPStatus.BAD_REQUEST
    except werkzeug.exceptions.BadRequestKeyError as e:
        return {'message': 'Invalid or missing key name. Required options: name, synopsis, image, total_episodes, is_movie, is_dubbed, genres.'}, HTTPStatus.BAD_REQUEST
    except sqlalchemy.exc.IntegrityError as e:
        if type(e.orig) == psycopg2.errors.UniqueViolation:
            return {'message': 'Anime already registered!'}, HTTPStatus.CONFLICT


# ​
# **Rota protegida** - Apenas um mod ou adm podem acessar a rota

# É preciso que os gêneros sejam mapeados para fazer a relação. Corpo da requisição:
# ​Erro se db estiver vazio
# ```json
# {
#   "name": "Kobayashi-san Chi no Maid Dragon S",
#   "synopsis": "Kobayashi é uma funcionária comum que leva uma vida bem banal e mora sozinha em um pequeno apartamento – até que ela salva a vida de um dragão fêmea em apuros.",
#   "image_url": "https://i.imgur.com/nriTGmm.jpg",
#   "total_episodes": 12,
#   "is_movie": false,
#   "is_dubbed": false,
#   "genres": ["Slice of Life", "Comédia", "Fantasia"],
#   "created_at": "2021-10-03 14:56:17"
# }
