from werkzeug.datastructures import FileStorage
from os import getenv
import requests


def upload_image(image: FileStorage) -> str:
    url = 'https://api.imgur.com/3/upload'
    data = {'image': image}
    headers = {'Authorization': 'Client-ID {}'.format(getenv('IMGUR_CLIENT_ID'))}

    r = requests.post(url, files=data, headers=headers)

    return r.json()['data']['link']
