# route.py

from re import I
from wtforms.fields.simple import SubmitField
from app.datasubsets.forms import ChooseSubsetForm, dataSubSet
from datetime import datetime
import os
import json
import logging
from pprint import pprint
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
    session,
    abort,
    send_from_directory
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from guess_language import guess_language
from app import db, logging
from app.models import User, Post, Entity
from app.vis import bp
import app.mdb
from wtforms import TextAreaField, SubmitField


@bp.route("/vis", methods=["GET", "POST"])
@login_required
def vis():

    current_app.logger.warn('vis')

    return render_template(
        "vis.html",
    )

@bp.route("/vis-icdc", methods=["GET", "POST"])
@login_required
def visicdc():

    current_app.logger.warn('vis')
    s = os.environ.get("NEO4J_MDB_URI")
    u = os.environ.get("NEO4J_MDB_USER")
    p = os.environ.get("NEO4J_MDB_PASS")

    return render_template(
        "vis-icdc.html",  s=s, u=u, p=p
    )

@bp.route("/vis-ctdc", methods=["GET", "POST"])
@login_required
def visctdc():

    current_app.logger.warn('vis')
    s = os.environ.get("NEO4J_MDB_URI")
    u = os.environ.get("NEO4J_MDB_USER")
    p = os.environ.get("NEO4J_MDB_PASS")

    return render_template(
        "vis-ctdc.html",  s=s, u=u, p=p
    )

@bp.route("/vis-bento", methods=["GET", "POST"])
@login_required
def visbento():

    current_app.logger.warn('vis')
    s = os.environ.get("NEO4J_MDB_URI")
    u = os.environ.get("NEO4J_MDB_USER")
    p = os.environ.get("NEO4J_MDB_PASS")

    return render_template(
        "vis-bento.html", s=s, u=u, p=p
    )


@bp.route("/graphvis", methods=["GET", "POST"])
@login_required
def graphvis():

    current_app.logger.warn('graphvis')

    return render_template(
        "graphvis.html",
    )