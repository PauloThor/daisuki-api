from app.controllers.user_controller import create, delete, update
from flask import Blueprint

bp = Blueprint('users', __name__, url_prefix='/users')

bp.post('')(create)
bp.patch('/<int:id>')(update)
bp.delete('/<int:id>')(delete)