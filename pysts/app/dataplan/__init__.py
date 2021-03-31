from flask import Blueprint

bp = Blueprint("dataplan", __name__)

from app.dataplan import routes
