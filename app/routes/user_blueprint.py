from app.controllers.user_controller import create, login, update
from flask import Blueprint

bp = Blueprint('users', __name__, url_prefix='/users')

bp.post('')(create)
bp.post('/login')(login)
bp.put('/update')(update)