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
from app import db, logging
from app.models import User, Post, Entity
from app.ver import bp
import app.mdb
from app.ver.forms import ModelVersioningForm
from wtforms import TextAreaField, SubmitField


@bp.route("/versioning", methods=["GET", "POST"])

def versioning():

    current_app.logger.warn('versioning')

    m = app.mdb.mdb()
    optgroup_ = m.get_dataset_tag_choices()

    versionform = ModelVersioningForm()
    versionform.releases.choices = optgroup_

    return render_template(
        "version-history-report.html",
        form=versionform)


def versioningicdc():

    current_app.logger.warn('versioning')

    formdata = None
    versionform = ModelVersioningForm()

    if versionform.validate_on_submit():
        if versionform.report_format.data == "json":
            return current_app.send_static_file('icdc-history.json')


    return render_template(
        "version-history.html",
        form=versionform)
