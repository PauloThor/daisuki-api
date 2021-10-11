from flask import Flask
from flask_cors import CORS

def init_app(app: Flask):
    CORS(app, origins=['http://localhost:5000'], methods=["GET", "POST", "PATCH", "DELETE"])

    