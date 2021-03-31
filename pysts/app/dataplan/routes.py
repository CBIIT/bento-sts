# route.py

from datetime import datetime
import os
import json
import pprint
from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
    g,
    jsonify,
    current_app,
    Response,
    abort,
    send_from_directory
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from guess_language import guess_language
from app import db, logging
from app.models import User, Post, Entity
from app.dataplan import bp
import app.mdb


@bp.route("/dataplan", methods=["GET", "POST"])
@login_required
def index():

    current_app.logger.warn('...dataplan...')
    m = app.mdb.mdb()
    plan_ = m.get_dataplan('ICDC')

    current_app.logger.warn('got... {}'.format(plan_))

    return render_template(
        "submitted_tags.html",
        model='ICDC',
        formatted_tags=plan_
    )
