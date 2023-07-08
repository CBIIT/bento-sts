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
import flask_excel
from werkzeug.utils import secure_filename
from guess_language import guess_language
from app import db, logging
from app.datasubsets.forms import ChooseSubsetForm, gammaSubsetForm, deltaOneForm, deltaTwoForm
from app.models import User, Post, Entity
from app.datasubsets import bp
from app.datasubsets.decon import get_model_and_tag
import app.mdb
from wtforms import TextAreaField, SubmitField





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

@bp.route("/datasubsets", defaults={'datasubsetid': None}, methods=["GET", "POST"])
@bp.route("/datasubsets/<datasubsetid>", methods=["GET", "POST"])
@login_required
def datasubsets(datasubsetid):

    print('=-=-=-=-=-=-=-=-=-=-=-==-=-=-\n\n')
    current_app.logger.warn('Gamma> datasubsetid is {}'.format(datasubsetid))

    model_ = None
    dataplan_ = None
    tag_ = None

    m = app.mdb.mdb()
    optgroup_ = m.get_dataset_tag_choices()

    tagform = gammaSubsetForm()
    
    tagform.datasubsets.choices = optgroup_

    if request.method == 'GET':
        print('Gamma> GET 10 logging, now looking for datasubset {}'.format(datasubsetid))
        current_app.logger.warn('Gamma> 11datasubsetid is {}'.format(datasubsetid))

        if datasubsetid is None:
            datasubsetid = session['datasubset']
        
        if (datasubsetid):
            tagform.datasubsets.data = datasubsetid
            model_, tag_ = get_model_and_tag(datasubsetid)
            print('Gamma GET logging, now looking for model {} and tag {}'.format(model_, tag_))
            dataplan_ = m.get_dataset(dataset=tag_, model=model_)
            print('Gamma GET logging, now HAVE for A model {} and tag {}'.format(model_, tag_))
            session['tag_'] = tag_
            session['model_'] = model_
            session['datasubset'] = datasubsetid
            current_app.logger.warn(' .. Gamma GET point datasubsets... got... {}'.format(dataplan_))

    if tagform.validate_on_submit():

        if tagform.submit.data:
            datasubsetid = tagform.datasubsets.data
            model_, tag_ = get_model_and_tag(datasubsetid)
            session['datasubset'] = datasubsetid
            #print('logging, now looking for model {} and tag {}'.format(model_, tag_))
            #if model is None:
            #    model = 'All Model'
            plan_ = m.get_dataset_tags(dataset=tag_, model=model_)
            current_app.logger.warn(' .. point submit... got... {}'.format(plan_))

        if tagform.submit.data:
            datasubsetid = tagform.datasubsets.data
            model_, tag_ = get_model_and_tag(datasubsetid)
            session['datasubset'] = datasubsetid
            print('Gamma POST logging, now looking for model {} and tag {}'.format(model_, tag_))
            dataplan_ = m.get_dataset(dataset=tag_, model=model_)
            print('Gamma POST logging, now HAVE for A model {} and tag {}'.format(model_, tag_))
            session['tag_'] = tag_
            session['model_'] = model_
            session['datasubset'] = datasubsetid
            current_app.logger.warn(' .. Gamma POST point datasubsets... got... {}'.format(dataplan_))
            return redirect(url_for('datasubsets.datasubsets', datasubsetid=datasubsetid))

        if (tagform.exportcsv.data):
            print('hello there csv!')
            #return render_template("export-csv.html")
            model_, tag_ = get_model_and_tag(tagform.datasubsets.data)
            print('Gamma CSV logging, now looking for model {} and tag {}'.format(model_, tag_))
            dataplan_ = m.get_dataset(dataset=tag_, model=model_)

            print('>git ut<')
            print('Gamma CSV logging, now HAVE for A model {} and tag {}'.format(model_, tag_))
            session['tag_'] = tag_
            session['model_'] = model_
            session['datasubset'] = tagform.datasubsets.data
            current_app.logger.warn(' .. Gamma CSV point datasubsets... got... {}'.format(dataplan_))
            return flask_excel.make_response_from_array(dataplan_, "csv")

        if (tagform.exportjson.data):
            print('general kenobi')
            #return render_template("export-json.html")
            return current_app.send_static_file('dataset-export.json')
        if (tagform.exportyaml.data):
            print('general kenobi')
            #return render_template("export-json.html")
            return current_app.send_static_file('dataset-export.yml')
        if (tagform.exportxlsx.data):
            print('xlsx')
            #return render_template("export-json.html")
            return current_app.send_static_file('dataset-export.xlsx')
                

    print('Gamma < end')
    return render_template(
        "datasubsets.html",
        form=tagform,
        tag=tag_,
        model=model_,
        formatted_dataset=dataplan_
    )

@bp.route("/tag-delta", methods=["GET", "POST"])
@login_required
def tagdelta():

    # notice
    import pprint
    dump_a = request.form.to_dict()
    pprint.pprint('dump_a got back {}'.format(dump_a))

    model_a = None
    plan_a = None
    tag_a = None
    model_b = None
    plan_b = None
    tag_b = None
    newtagid = None


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
    #oneform.entire_model.choices = possible_avail_models_

    class F(deltaTwoForm):
        pass

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
                session['tag_a'] = tag_a
            if (oneform.bset.data):
                model_b, tag_b = get_model_and_tag(oneform.bset.data)
                print('logging, now looking for model {} and tag {}'.format(model_b, tag_b))
                plan_b = m.get_dataset_tags(dataset=tag_b, model=model_b)
                print('logging, now HAVE for model {} and tag {}'.format(model_b, tag_b))
                session['tag_b'] = tag_b
                print('--------')
                print('plan_b is {}'.format(plan_b))

                if 'submitter' in plan_b:
                    for datatag in plan_b['submitter']:
                        nanoid = datatag[3]
                        print('test >> {}'.format(nanoid))
                        setattr(F, str(nanoid), SubmitField(label="Add"))

        if (oneform.create.data):
            tag = oneform.newsubset_tag.data.strip()
            if (oneform.newsubset_model.data is not None and tag is not None and tag != ''):
                newtagid = m.create_submitter_tag_for_model(oneform.newsubset_model.data, oneform.newsubset_tag.data)
                print('logging, created new tag {}'.format(newtagid))
                return redirect(url_for('datasubsets.tagdelta'))

    formb = F()

    if formb.validate_on_submit():
        print('  YAHOOO ')
        print('session a is for {}'.format(session['tag_a']))
        print('session b is for {}'.format(session['tag_b']))

    return render_template(
        "edit.html",
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
    

@bp.route("/datasubsets/edit", methods=["GET", "POST"])
@login_required
def edit():

    # notice
    import pprint
    dump_a = request.form.to_dict()
    pprint.pprint('dump_a got back {}'.format(dump_a))

    model_a = None
    plan_a = None
    tag_a = None
    model_b = None
    plan_b = None
    tag_b = None
    newtagid = None
    entire_model = None

    ## now populate formA and formB if in session
    model_a = session.pop('model_a', None)
    tag_a = session.pop('tag_a', None)
    model_b = session.pop('model_b', None)
    tag_b = session.pop('tag_b', None)
    
    if 'entire_model' in session:
        entire_model = session['entire_model']

    if (1):
        current_app.logger.info(' logging point E--13 ')
        print('model_a {} '.format(model_a))
        print('model_b {} '.format(model_b))
        print('tag_a {} '.format(tag_a))
        print('tag_b {} '.format(tag_b))
        print('entire_model {}'.format(entire_model))

    m = app.mdb.mdb()
    optgroup_ = m.get_dataset_tag_choices()
    avail_models_ = m.get_list_of_models()
    #print('logging, point Y now looking for list {} '.format(avail_models_))

    oneform = deltaOneForm()
    oneform.aset.choices = optgroup_
    oneform.bset.choices = optgroup_
    possible_avail_models_ = [(x, x) for x in avail_models_]
    possible_avail_models_ = tuple(possible_avail_models_)    
    oneform.newsubset_model.choices = possible_avail_models_
    oneform.entire_model.choices = possible_avail_models_

    print('logging point E--7')

    ## coming back around, now load the dataset tables....
    if (tag_a):
        #print('logging, now looking for model {} and tag {}'.format(model_a, tag_a))
        plan_a = m.get_dataset_tags(dataset=tag_a, model=model_a)
        #print('logging, now HAVE for model {} and tag {}'.format(model_a, tag_a))
        session['tag_a'] = tag_a
        session['model_a'] = model_a
        if 'choice_a' in session:
            oneform.aset.data = session['choice_a']
        print('logging point E--6')

    if (tag_b) and (tag_b != 'all'):
        #print('logging, now looking for model {} and tag {}'.format(model_b, tag_b))
        plan_b = m.get_dataset_tags(dataset=tag_b, model=model_b)
        #print('logging, now HAVE for model {} and tag {}'.format(model_b, tag_b))
        session['tag_b'] = tag_b
        session['model_b'] = model_b
        if 'choice_b' in session:
            oneform.bset.data = session['choice_b']
        print('logging point E--5')

    if (entire_model) and (tag_b == 'all'): 
        session['tag_b'] = tag_b
        session['model_b'] = model_b
        session['entire_model'] = entire_model
        oneform.entire_model.data = model_b
        plan_b = m.get_dataset_tags(dataset=tag_b, model=model_b)
        print('logging point E--4')


    if (1):
        current_app.logger.info(' logging point E--3 ')
        print('model_a {} '.format(model_a))
        print('model_b {} '.format(model_b))
        print('tag_a {} '.format(tag_a))
        print('tag_b {} '.format(tag_b))
        print('entire_model {}'.format(entire_model))

    pprint.pprint(' E0 >> ')

    pprint.pprint(oneform)
    pprint.pprint(' E0.1 ')
    pprint.pprint(optgroup_)

    if oneform.validate_on_submit():

        pprint.pprint(' E1 >> ')

        if (0):
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

            print('dumping oneform')
            print('done.')

        pprint.pprint(' E2 ')

        if (oneform.submit.data):
            pprint.pprint(' E3 ')
            # hack as a way to extract the model and tag from the choice/html form
            if (1):
                print('GOOD VALIDATION')

                print(' ... A choice data {}'.format(oneform.aset.data))
                print(' ... A choice label {}'.format(oneform.aset.label))
                print(' ... A choice name {}'.format(oneform.aset.name))
                print(' ... A choice raw_data {}'.format(oneform.aset.raw_data))
                print(' ... A choice object_data {}'.format(oneform.aset.object_data))
                print(' ... A choice shortname {}'.format(oneform.aset.type))
                print(' ... A choice type {}'.format(oneform.aset.short_name))
                print(' ... A choice id {}'.format(oneform.aset.id))

            if (oneform.aset.data):
                model_a, tag_a = get_model_and_tag(oneform.aset.data)
                print('logging, now looking for model {} and tag {}'.format(model_a, tag_a))
                plan_a = m.get_dataset_tags(dataset=tag_a, model=model_a)
                print('logging, now HAVE for A model {} and tag {} and id {}'.format(model_a, tag_a, oneform.aset.id))
                session['tag_a'] = tag_a
                session['model_a'] = model_a
                session['choice_a'] = oneform.aset.data

            if (oneform.bset.data):
                model_b, tag_b = get_model_and_tag(oneform.bset.data)
                #print('logging, now looking for model {} and tag {}'.format(model_b, tag_b))
                plan_b = m.get_dataset_tags(dataset=tag_b, model=model_b)
                #print('logging, now HAVE for model {} and tag {}'.format(model_b, tag_b))
                session['tag_b'] = tag_b
                session['model_b'] = model_b
                session['choice_b'] = oneform.bset.data
                session['entire_model'] = None
                
        pprint.pprint(' E4 ')

        if 'entire' in request.form:
            pprint.pprint(' E5 ')
            if request.form['entire'] == 'Get Model':
                #tag = oneform.newsubset_tag.data.strip()
                model_b = oneform.entire_model.data
                tag_b = "all"
                print('logging that we should look for ENTIRE model {}'.format(model_b))
                plan_b = m.get_dataset_tags(dataset="all", model=model_b)
                session['tag_b'] = tag_b
                session['model_b'] = model_b
                session['entire_model'] = model_b
                session['choice_b'] = oneform.bset.data
                pprint.pprint(' E8 ')

        pprint.pprint(' E7 ')

        if (oneform.create.data):
            print.pprint(' E8 ')
            tag = oneform.newsubset_tag.data.strip()
            if (oneform.newsubset_model.data is not None and tag is not None and tag != ''):
                newtagid = m.create_submitter_tag_for_model(oneform.newsubset_model.data, oneform.newsubset_tag.data)
                print('logging, created new tag {}'.format(newtagid))
                return redirect(url_for('datasubsets.edit'))

        #if (oneform.getmodel.data):
        #    tag_b = 'all'
        #    model_b = oneform.getmodel.data
        #    plan_b = m.get_dataset_tags(dataset=tag_b, model=model_b)
        #    session['tag_b'] = tag_b
        #    session['model_b'] = model_b

        pprint.pprint(' E10 >> ')

    pprint.pprint(' E11 ')
    print(' tag_a is {} '.format(tag_a))
    print(' tag_b is {} '.format(tag_b))
    print('model_a {} '.format(model_a))
    print('model_b {} '.format(model_b))
    print('entire_model {}'.format(entire_model))

    print(' new model id is {} '.format(oneform.newsubset_model.data))
    print(' new tag id is {} '.format(oneform.newsubset_tag.data))
    print(' entire model id is {} '.format(oneform.entire_model.data))
    
    current_app.logger.info(' logging point E13 ')    

    return render_template(
        "edit.html",
        form=oneform,
        extra="zeta",
        taga=tag_a,
        modela=model_a,
        formatteda=plan_a,
        tagb=tag_b,
        modelb=model_b,
        formattedb=plan_b,
        newtagid=newtagid
    )



@bp.route("/datasubsets/act", methods=["GET", "POST"])
@login_required
def act():

    print('\n\nstarting \choose')

    if request.method == 'POST':
        if 'submit' in request.form:
            alpha = request.form['submit']
            print('alpha is {}'.format(alpha))
        if 'create' in request.form:
            alpha = request.form['create']
            print('alpha is {}'.format(alpha))
        #if 'entire' in request.form:
        #    alpha = request.form['create']
        #    print('alpha is {}'.format(alpha))


    # notice
    #import pprint
    #pprint.pprint(request.form)
    #pprint.pprint(dir(request.form))
    #print('goodsdfajsdlfjaslkdfjal')
    
    #dump_a = request.form.to_dict()
    #pprint.pprint('dump_a got back {}'.format(dump_a))

    model_a = None
    plan_a = None
    tag_a = None
    model_b = None
    plan_b = None
    tag_b = None
    newtagid = None

    print('logging point T--1')

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
    oneform.entire_model.choices = possible_avail_models_
    
    print('logging point T0')

    if oneform.validate_on_submit():

        print('\nlogging point T1\n')

        if (1):
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

            print(' ... create data {}'.format(oneform.entire.data))
            print(' ... create label {}'.format(oneform.entire.label))

            print('dumping oneform')
            print('done.')

        if (oneform.submit.data):
            # hack as a way to extract the model and tag from the choice/html form
            if (1):
                print('GOOD VALIDATION')

                print(' ... A choice data {}'.format(oneform.aset.data))
                print(' ... A choice label {}'.format(oneform.aset.label))
                print(' ... A choice name {}'.format(oneform.aset.name))
                print(' ... A choice raw_data {}'.format(oneform.aset.raw_data))
                print(' ... A choice object_data {}'.format(oneform.aset.object_data))
                print(' ... A choice shortname {}'.format(oneform.aset.type))
                print(' ... A choice type {}'.format(oneform.aset.short_name))
                print(' ... A choice id {}'.format(oneform.aset.id))

            if (oneform.aset.data):
                model_a, tag_a = get_model_and_tag(oneform.aset.data)
                print('logging, now looking for model {} and tag {}'.format(model_a, tag_a))
                plan_a = m.get_dataset_tags(dataset=tag_a, model=model_a)
                print('logging, now HAVE for A model {} and tag {} and id {}'.format(model_a, tag_a, oneform.aset.id))
                session['tag_a'] = tag_a
                session['model_a'] = model_a
                session['choice_a'] = oneform.aset.data

            if (oneform.bset.data):
                model_b, tag_b = get_model_and_tag(oneform.bset.data)
                print('logging, now looking for model {} and tag {}'.format(model_b, tag_b))
                plan_b = m.get_dataset_tags(dataset=tag_b, model=model_b)
                print('logging, now HAVE for model {} and tag {}'.format(model_b, tag_b))
                session['tag_b'] = tag_b
                session['model_b'] = model_b
                session['choice_b'] = oneform.bset.data
                session['entire_model'] = None

        if 'entire' in request.form:
            print('.. detected entire')
            if (request.form['entire']):
                #tag = oneform.newsubset_tag.data.strip()
                model_b = oneform.entire_model.data
                tag_b = "all"
                print('logging that we should look for ENTIRE model {}'.format(model_b))
                plan_b = m.get_dataset_tags(dataset="all", model=model_b)
                session['tag_b'] = tag_b
                session['model_b'] = model_b
                session['entire_model'] = model_b
                session['choice_b'] = oneform.bset.data

        if (oneform.create.data):
            tag = oneform.newsubset_tag.data.strip()
            if (oneform.newsubset_model.data is not None and tag is not None and tag != ''):
                newtagid = m.create_submitter_tag_for_model(oneform.newsubset_model.data, oneform.newsubset_tag.data)
                print('logging, created new tag {}'.format(newtagid))
                return redirect(url_for('datasubsets.edit'))          

        print('logging point T3')

    print('logging point T4')

    return redirect(url_for('datasubsets.edit'))

@bp.route("/datasubsets/add", methods=["GET", "POST"])
@login_required
def add():    

    print('logging point A0')

    current_app.logger.info('Datasubset Add')
    current_app.logger.info('request_url is {}'.format(request.url))
     
    add_id = None
    aset = None
    tag_a = None
    model_a = None
    bset = None
    bnode = None
    tag_b = None
    model_b = None

    add_from_model = False

    add_id = request.args.get('add_id', None)
    aset = request.args.get('aset', None)
    bset = request.args.get('bset', None)
    bnode = request.args.get('bnode', None)
    entire = request.args.get('entire', None)
    
    print('logging point A3')


    if (entire):
        #if entire > 0:
        add_from_model = True
        model_b = bset
        print(' A: -3')
    #if 'entire_model' in session:
    #    add_from_model = True
    #    model_b = bset
    #    print(' A: -2')
    if tag_b == 'all':
        add_from_model = True
        model_b = bset
        print(' A: -1')

    if (aset):
        current_app.logger.debug('add: aset is {}'.format(aset))
    if (bset):
        current_app.logger.debug('add: bset is {}'.format(bset))
    
    print('logging point A4')
    print('model_a {}'.format(model_a))
    print('model_b {}'.format(model_b))

    if add_id:
        current_app.logger.debug('add: add_id is {}'.format(add_id))
    
    if aset:
        current_app.logger.debug('add: aset is {}'.format(aset))
        model_a, tag_a = get_model_and_tag(aset)
        session['tag_a'] = tag_a
        session['model_a'] = model_a
        current_app.logger.debug('add: a tag is {}'.format(tag_a))
        current_app.logger.debug('add: a model is {}'.format(model_a))

    print('logging point A5')
    print('model_a {}'.format(model_a))
    print('model_b {}'.format(model_b))
    print('add_from_model {}'.format(add_from_model))

    if (add_from_model == False) and (bset):
        print('logging point A6')
        current_app.logger.debug('add: bset is {}'.format(bset))
        model_b, tag_b = get_model_and_tag(bset)
        session['tag_b'] = tag_b
        session['model_b'] = model_b
        current_app.logger.debug('add: b tag is {}'.format(tag_b))
        current_app.logger.debug('add: b node is {}'.format(bnode))
        current_app.logger.debug('add: b model is {}'.format(model_b))

    print('logging point A10')
    print('model_a {}'.format(model_a))
    print('model_b {}'.format(model_b))
    print('tag_a {}'.format(tag_a))
    print('tag_b {}'.format(tag_b))
    print('add_from_model{}'.format(add_from_model))

    if (model_a != model_b):
        flash('Both Models must be the same')
        return redirect(url_for('datasubsets.edit'))

    if ( add_from_model is False) and (tag_a == tag_b):
        current_app.logger.debug('add: tag_a {} tab_b {} and model_a {} and model_b {}'.format(tag_a, tag_b, model_a, model_b))
        flash('Sorry Charlie, not adding from dataset back to itself (choose 2 different datasets from same model)')
        return redirect(url_for('datasubsets.edit'))



    m = app.mdb.mdb()
    m.add_submitter_tag_for_model_prop(model=model_a, nodenanoid=bnode, propnanoid=add_id, tag=tag_a)

    current_app.logger.debug('Add: Leaving')

    return redirect(url_for('datasubsets.edit'))

@bp.route("/datasubsets/remove", methods=["GET", "POST"])
@login_required
def remove():    

    current_app.logger.info('START REMOVE')
    current_app.logger.info('Datasubset Add')
    current_app.logger.info('request_url is {}'.format(request.url))
     
    remove_id = None
    aset = None
    anode = None
    tag_a = None
    model_a = None
    bset = None
    tag_b = None
    model_b = None

    remove_id = request.args.get('remove_id', None)
    aset = request.args.get('aset', None)
    anode = request.args.get('anode', None)
    bset = request.args.get('bset', None)
    if (aset):
         current_app.logger.debug('remove: aset is {}'.format(aset))
    if (anode):
         current_app.logger.debug('remove: anode is {}'.format(anode))
    if (bset):
         current_app.logger.debug('remove: bset is {}'.format(bset))

    
    if remove_id:
        current_app.logger.debug('remove: add_id is {}'.format(remove_id))
    
    if aset:
        current_app.logger.debug('remove: aset is {}'.format(aset))
        model_a, tag_a = get_model_and_tag(aset)
        session['tag_a'] = tag_a
        session['model_a'] = model_a
        current_app.logger.debug('remove: a tag is {}'.format(tag_a))
        current_app.logger.debug('remove: a model is {}'.format(model_a))
    
    #if bset:
    #    current_app.logger.debug('remove: bset is {}'.format(bset))
    #    model_b, tag_b = get_model_and_tag(bset)
    #    session['tag_b'] = tag_b
    #    session['model_b'] = model_b
    #    current_app.logger.debug('remove: b tag is {}'.format(tag_b))
    #    current_app.logger.debug('remove: b model is {}'.format(model_b))

    if (remove_id is not None and tag_a is not None and model_a is not None and anode is not None):
        m = app.mdb.mdb()
        m.remove_submitter_tag_for_model_prop(model=model_a, nodenanoid=anode,  propnanoid=remove_id, tag=tag_a)


    current_app.logger.debug('remove: Leaving')

    return redirect(url_for('datasubsets.edit'))