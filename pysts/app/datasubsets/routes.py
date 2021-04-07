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
from app.datasubsets import bp
import app.mdb


@bp.route("/datasubsets", methods=["GET", "POST"])
@login_required
def index():

    current_app.logger.warn('...data subsets...')
    m = app.mdb.mdb()
    plan_ = m.get_tags('ICDC')

    current_app.logger.warn('got... {}'.format(plan_))

    return render_template(
        "tags.html",
        model='ICDC',
        formatted_tags=plan_
    )

@bp.route("/tags", methods=["GET", "POST"])
@login_required
def tags():

    model = request.args.get("model")    # to filter by model
    current_app.logger.warn('looking for model ... {}'.format(model))

    m = app.mdb.mdb()
    plan_ = m.get_tags(model)

    current_app.logger.warn('point 4 got... {}'.format(plan_))
    if model is None:
        model = 'All Model'

    return render_template(
        "tags.html",
        model=model,
        formatted_tags=plan_
    )
