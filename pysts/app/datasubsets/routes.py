# route.py

from app.datasubsets.forms import ChooseSubsetForm
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
from app.datasubsets.forms import ChooseSubsetForm, gammaSubsetForm
from app.models import User, Post, Entity
from app.datasubsets import bp
from app.datasubsets.decon import get_model_and_tag
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
        extra='A',
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
        extra="B",
        model=model,
        formatted_tags=plan_
    )

@bp.route("/tagbeta", methods=["GET", "POST"])
@login_required
def tagbeta():

    model = None
    plan_ = None

    m = app.mdb.mdb()

    tagform = ChooseSubsetForm()

    if tagform.validate_on_submit():
        model = tagform.datasubsets.data

        if model is None:
            model = 'All Model'
        plan_ = m.get_tags(model)

        current_app.logger.warn('point 4 got... {}'.format(plan_))

    return render_template(
        "tagbeta.html",
        form=tagform,
        extra="C",
        model=model,
        formatted_tags=plan_
    )


@bp.route("/tag-gamma", methods=["GET", "POST"])
@login_required
def taggamma():

    model_ = None
    plan_ = None
    tag_ = None

    m = app.mdb.mdb()
    optgroup_ = m.get_dataset_tag_choices()

    optgroup = (
        ('ICDC', (
            ('apple', 'Apple'),
            ('peach', 'Peach'),
            ('pear', 'Pear')
        )),
        ('CTDC', (
            ('cucumber', 'Cucumber'),
            ('potato', 'Potato'),
            ('tomato', 'Tomato'),
        )),
        ('Test', (()))
    )

    optgroup2 = (
        ('ICDC', (
            ('apple', 'Apple'),
            ('peach', 'Peach'),
            ('pear', 'Pear'),
        )),
        ('CTDC', (
            ('cucumber', 'Cucumber'),
            ('potato', 'Potato'),
            ('tomato', 'Tomato'),
        )),
        ('Test', (()))
    )

    # optgroup3 = ('ICDC', (('GLIOMA01', 'GLIOMA01'), ('NCATS-COP01', 'NCATS-COP01'), ('UBC01', 'UBC01'), ('UBC02', 'UBC02')))

    optgroup3 = ( 
        ('ICDC', (
            ('GLIOMA01', 'GLIOMA01'), 
            ('NCATSCOP01', 'NCATSCOP01'), 
            ('UBC01', 'UBC01'),
            ('UBC02', 'UBC02'),
        )),
        ('Test', (()))
    )

    optgroup4 = ( 
        ('ICDC', (
            ('GLIOMA01', 'GLIOMA01'), 
            ('NCATSCOP01', 'NCATSCOP01'), 
            ('UBC01', 'UBC01'),
            ('UBC02', 'UBC02'),
        )),
        
    )

    optgroup5 = ( 
        ('ICDC', (
            ('GLIOMA01', 'GLIOMA01'), 
            ('NCATS-COP01', 'NCATS-COP01'), 
            ('UBC01', 'UBC01'),
            ('UBC02', 'UBC02'),
        )),
        
    )

    optgroup6 = ( 
        ('ICDC', (
            ('GLIOMA01', 'GLIOMA01'), 
            ('NCATS-COP01', 'NCATS-COP01'), 
            ('UBC01', 'UBC01'),
            ('UBC02', 'UBC02'),
        )),
        
    )

    tagform = gammaSubsetForm()
    
    #tagform.datasubsets.choices = optgroup_
    #tagform.datasubsets.choices = optgroup6
    tagform.datasubsets.choices = optgroup_

    if tagform.validate_on_submit():

        if (0):
            #model = tagform.datasubsets.data
            #model_ = tagform.datasubsets.data.label
            import pprint
            pprint.pprint(dir(tagform.datasubsets))
            print("\ndata is ")
            pprint.pprint(tagform.datasubsets.data)
            print("\nid is ")
            pprint.pprint(tagform.datasubsets.id)
            print("\nchoice_values is ")
            pprint.pprint(tagform.datasubsets.choice_values)
            print("\nname is ")
            pprint.pprint(tagform.datasubsets.name)
            print("\nlabel is ")
            pprint.pprint(tagform.datasubsets.label)
            print("\nmeta is ")
            pprint.pprint(tagform.datasubsets.meta)
            print("\noption_widget is ")
            pprint.pprint(tagform.datasubsets.option_widget)
            print("\nraw_Data is ")
            pprint.pprint(tagform.datasubsets.raw_data)
            print("\ngettext is ")
            pprint.pprint(tagform.datasubsets.gettext)

        model_, tag_ = get_model_and_tag(tagform.datasubsets.data)
        print('logging, now looking for model {} and tag {}'.format(model_, tag_))
        #if model is None:
        #    model = 'All Model'
        plan_ = m.get_dataset_tags(dataset=tag_, model=model_)

        #current_app.logger.warn('point 4 got... {}'.format(plan_))

    return render_template(
        "tag-gamma.html",
        form=tagform,
        extra="D",
        model=model_,
        formatted_tags=plan_
    )