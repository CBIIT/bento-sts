from flask import Blueprint

bp = Blueprint("datasubset", __name__)

from app.datasubsets import routes
