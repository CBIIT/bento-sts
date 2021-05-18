# route.py

from wtforms.fields.simple import SubmitField
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
from app.datasubsets.forms import ChooseSubsetForm, gammaSubsetForm, deltaOneForm, deltaTwoForm
from app.models import User, Post, Entity
from app.datasubsets import bp
from app.datasubsets.decon import get_model_and_tag
import app.mdb
from wtforms import TextAreaField, SubmitField



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


@bp.route("/tag-select", methods=["GET", "POST"])
@login_required
def tagselect():

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
        "tag-select.html",
        form=tagform,
        extra="G",
        model=model_,
        formatted_tags=plan_
    )

@bp.route("/tag-delta", methods=["GET", "POST"])
@login_required
def tagdelta():

    model_a = None
    plan_a = None
    tag_a = None
    model_b = None
    plan_b = None
    tag_b = None
    newtagid = None

    class F(deltaTwoForm):
        pass

    m = app.mdb.mdb()
    optgroup_ = m.get_dataset_tag_choices()
    avail_models_ = m.get_list_of_models()
    print('logging, point Y now looking for list {} '.format(avail_models_))

    oneform = deltaOneForm()
    oneform.aset.choices = optgroup_
    oneform.bset.choices = optgroup_
    possible_avail_models_ = [(x, x) for x in avail_models_]
    possible_avail_models_ = tuple(possible_avail_models_)    
    oneform.newsubset_model.choices = possible_avail_models_
    
    print('logging point Z')

    if oneform.validate_on_submit():
        print(' ... submit data {}'.format(oneform.submit.data))
        print(' ... submit label {}'.format(oneform.submit.label))
        print(' ... submit name {}'.format(oneform.submit.name))
        print(' ... submit raw_data {}'.format(oneform.submit.raw_data))
        print(' ... submit object_data {}'.format(oneform.submit.object_data))
        print(' ... submit shortname {}'.format(oneform.submit.type))
        print(' ... submit type {}'.format(oneform.submit.short_name))
    
        print(' ... create data {}'.format(oneform.create.data))
        print(' ... create label {}'.format(oneform.create.label))
        print(' ... create name {}'.format(oneform.create.name))
        print(' ... create raw_data {}'.format(oneform.create.raw_data))
        print(' ... create object_data {}'.format(oneform.create.object_data))
        print(' ... create shortname {}'.format(oneform.create.type))
        print(' ... create type {}'.format(oneform.create.short_name))
    


        if (oneform.submit.data):
            # hack as a way to extract the model and tag from the choice/html form
            print('GOOD VALIDATION')
            if (oneform.aset.data):
                model_a, tag_a = get_model_and_tag(oneform.aset.data)
                print('logging, now looking for model {} and tag {}'.format(model_a, tag_a))
                plan_a = m.get_dataset_tags(dataset=tag_a, model=model_a)
                print('logging, now HAVE for model {} and tag {}'.format(model_a, tag_a))
            if (oneform.bset.data):
                model_b, tag_b = get_model_and_tag(oneform.bset.data)
                print('logging, now looking for model {} and tag {}'.format(model_b, tag_b))
                plan_b = m.get_dataset_tags(dataset=tag_b, model=model_b)
                print('logging, now HAVE for model {} and tag {}'.format(model_b, tag_b))

                print('--------')
                print('plan_b is {}'.format(plan_b))

                if 'submitter' in plan_b:
                    for datatag in plan_b['submitter']:
                        #print('====')
                        nanoid = datatag[3]
                        print('test >> {}'.format(nanoid))
                        setattr(F, str(nanoid), SubmitField(label="Add"))
                        #msg = TextAreaField(id=1,default="hi",_name="1")
                        #setattr(F, str("Add"), TextAreaField(description=str(nanoid)))

        if (oneform.create.data):
            tag = oneform.newsubset_tag.data.strip()
            if (oneform.newsubset_model.data is not None and tag is not None and tag != ''):
                newtagid = m.create_submitter_tag_for_model(oneform.newsubset_model.data, oneform.newsubset_tag.data)
                print('logging, created new tag {}'.format(newtagid))
                return redirect(url_for('datasubsets.tagdelta'))

    formb = F()

    if formb.validate_on_submit():
         print('  YAHOOO ')

    return render_template(
        "tag-delta.html",
        form=oneform,
        extra="D",
        taga=tag_a,
        modela=model_a,
        formatteda=plan_a,
        tagb=tag_b,
        modelb=model_b,
        formattedb=plan_b,
        newtagid=newtagid,
        formb=formb
    )


@bp.route("/tag-epsilon", methods=["GET", "POST"])
@login_required
def tagepsilon():

    model_ = None
    plan_ = None
    tag_ = None

    m = app.mdb.mdb()
    optgroup_ = m.get_submitter_tag_choices()

    tagform = gammaSubsetForm()
    
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
        "tag-epsilon.html",
        form=tagform,
        extra="epsilon",
        model=model_,
        formatted_tags=plan_
    )


@bp.route("/tag-phi", methods=["GET", "POST"])
@login_required
def tagphi():
    print('yup')

    return redirect(url_for('datasubsets.tagdelta'))

@bp.route("/tag-export", methods=["GET", "POST"])
@login_required
def tagexport():
        return render_template("tag-export.html")