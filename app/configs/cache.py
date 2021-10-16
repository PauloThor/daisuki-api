from flask import Flask
from cachelib import FileSystemCache

cache = FileSystemCache('./app/cache')

def init_app(app: Flask) -> None:
    app.cache = cache