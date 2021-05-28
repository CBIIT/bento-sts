from flask import Blueprint

bp = Blueprint("vis", __name__)

from app.vis import routes
