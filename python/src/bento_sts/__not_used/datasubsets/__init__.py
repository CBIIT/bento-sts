from flask import Blueprint

bp = Blueprint("datasubsets", __name__)

from app.datasubsets import routes
