from flask import Blueprint
from app.controllers import user_controller as Controller

bp = Blueprint('users', __name__, url_prefix='/users')

bp.post('')(Controller.create)
bp.get('/<int:id>')(Controller.get_user)
bp.get('')(Controller.get_users)
bp.post('/login')(Controller.login)
bp.patch('/update')(Controller.update)
bp.patch('/update-password')(Controller.update_password)
bp.delete('')(Controller.delete_self)
bp.delete('/<int:id>')(Controller.delete)
bp.put('/moderators')(Controller.promote)
bp.delete('/moderators')(Controller.demote)
bp.get('/moderators')(Controller.get_mods)

bp.put('/favorites/<int:anime_id>')(Controller.post_favorite)
bp.get('/favorites')(Controller.get_favorites)
bp.delete('/favorites/<int:anime_id>')(Controller.delete_favorite)
