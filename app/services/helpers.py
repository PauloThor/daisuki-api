from dataclasses import asdict
from math import ceil
import humps
from app.exc import InvalidImageError, PageNotFoundError
from app.exc.user_error import InvalidPermissionError
from flask import jsonify, request, current_app
from flask_mail import Message
from flask_jwt_extended import get_jwt_identity

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}


def check_file_extension(filename: str):
    try:
        file_extension = filename.split('.')[1].lower()
        is_allowed = file_extension in ALLOWED_IMAGE_EXTENSIONS
        if not is_allowed:
            raise InvalidImageError
    except IndexError:
        raise InvalidImageError


def verify_admin_mod():
    user_permission = get_jwt_identity()['permission']

    if user_permission != 'admin' and user_permission != 'mod':
        raise InvalidPermissionError


def paginate(data_list, per_page=12, page=1):
        per_page = int(request.args.get('per_page', per_page))
        page = int(request.args.get('page', page))
        last_page = ceil(len(data_list)/per_page)
        total = len(data_list)

        if last_page == 0:
            return {
                "page": page,
                "previous": None,
                "next": None,
                "total": total,
                "data": []
            }

        if page < 1 or page > last_page:
            raise PageNotFoundError(page)

        previous_page = None
        next_page = None

        if page < last_page:
            next_page = page + 1
        
        if page > 1:
            previous_page = page - 1
        
        data_list = [humps.camelize(asdict(data)) for data in data_list]
        
        return {
            "page": page,
            "previous": f'page={previous_page}&per_page={per_page}' if previous_page else previous_page,
            "next": f'page={next_page}&per_page={per_page}' if next_page else next_page,
            "total": total,
            "data": data_list[((page-1)*per_page):(page*per_page)]
        }


def send_temp_token(user, token):
    msg = Message('Recuperação de senha Daisuki', recipients=[user.email])
    msg.html = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <style>
        .container {
            color: #281528;
        }
        h1 {
            color: #d81e5b;
        }
        button {
            margin: 20px 0;
            width: 166px;
            height: 48px;
            border-radius: 8px;
            border: none;
            font-size: 16px;
            background-color: #b4184c;
            color: #edf5fd;
            font-weight: bolder;
        }
        button:hover {
            background-color: #d81e5b;
            cursor: pointer;
        }
        a {
            text-decoration: none;
            color: #d81e5b;
        }
        .daisuki {
            margin-top: 30px;
        }
        </style>
    </head>
    <body>
        <div class="container">
        <header>
            <h1>Olá, %s</h1>
        </header>
        <main>
            <p>
            Uma redefinição de senha foi solicitada para sua conta. Se foi você,
            siga o link abaixo:
            </p>
            <a href="https://animedaisuki.vercel.app/password-recovery/%d/%s" target="__blank"
            ><button>Clique aqui</button></a
            >

            <p>Se não foi você, ignore este e-mail.</p>
            <div class="daisuki">
            <p>Atenciosamente,</p>
            <a href="https://www.teste.vercel.app/" target="__blank"
                ><img src="https://i.imgur.com/FdxcJm7.png" alt="Anime Daisuki!"
            /></a>
            </div>
        </main>
        </div>
    </body>
    </html>"""%(user.username, user.id, token)
    current_app.mail.send(msg)


def decode_json(data: dict) -> dict:
    return humps.decamelize(data)


def encode_json(model) -> dict: 
    data = asdict(model)
    return jsonify(humps.camelize(data))


def encode_list_json(data: list) -> list:
    output = [humps.camelize(asdict(model)) for model in data]
    return jsonify(output)
