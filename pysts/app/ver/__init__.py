from flask import Blueprint

bp = Blueprint("ver", __name__)

from app.ver import routes
