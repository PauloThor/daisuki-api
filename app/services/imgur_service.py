from werkzeug.datastructures import FileStorage
from app.services.helpers import check_file_extension
from os import getenv
import requests


def upload_image(image: FileStorage) -> str:
    check_file_extension(image.filename)

    url = 'https://api.imgur.com/3/upload'
    data = {'image': image}

    r = requests.post(url, files=data)

    return r.json()['data']['link']
