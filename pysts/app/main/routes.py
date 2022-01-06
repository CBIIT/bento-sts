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
from flask_paginate import Pagination, get_page_parameter
from app import db, logging
from app.main.forms import SearchForm, SelectModelForm
# from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm, EditTermForm, DeprecateTermForm, DiffForm
# from app.main.forms import EditNodeForm, DeprecateNodeForm
# from app.main.forms import EditPropForm, DeprecatePropForm
from app.main.forms import SelectModelForm
import app.search
from app.main import bp
from app.util import get_yaml_for
from app.mdb import mdb
from app.arc import diff_mdf

@bp.before_app_request
def before_request():
    g.search_form = SearchForm()
    g.locale = 'EN_US'


@bp.route('/', methods=['GET', 'POST'])
@bp.route("/index", methods=["GET", "POST"])
def index():
    return render_template(
        "index.html",
        title="Home",
    )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@bp.route("/models/<name>")
@bp.route("/models")
def models(name=None):
    format = request.args.get("format")
    m = mdb()

    if name is not None:
        model_ = m.get_model_by_name(name)

        if format == 'yaml':
            yaml = get_yaml_for(model_.handle)
            return Response(yaml, mimetype='text/plain')

        else:
            return render_template(
                "mdb-model.html",
                title="Model: {}".format(model_.handle),
                mdb=model_,
                subtype="main.models",
                display="detail",
            )

    else:
        models_ = m.get_list_of_models()
        return render_template(
            "mdb-model.html",
            title="Models",
            mdb=sorted(models_, key=lambda x:x["name"]),
            subtype="main.models",
            display="list",
        )

@bp.route("/<entities>", defaults={'id': None}, methods=['GET', 'POST'])
@bp.route('/<entities>/<id>', methods=['GET', 'POST'])

def entities(entities, id):

    if request.form.get("format"):
        format = request.args.get("format")
    elif request.form.get("export"):
        format = "json"
    else:
        format = ""

    model = request.form.get("model_hdl")
    id_ = request.args.get("id")
    page = request.args.get(get_page_parameter(), type=int, default=1)
    select_form = SelectModelForm()
    select_form.model_hdl.choices = [(x['handle'],x['handle']) for x
                                     in current_app.config["MODEL_LIST"]]
    current_app.logger.info("model: {}, format: {}".format(model, format))
    current_app.logger.info(list(request.args.keys()))
    id = id
    if id is None:
        if id_ is not None:
            id = id_

    m = mdb()
    dispatch = {
        "nodes": {
            "title": "Node",
            "list_title": "Nodes",
            "template": "mdb-node.html",
            "subtype": "nodes",
            "sort_key": lambda x:x[1],
            "get_by_id": m.get_node_by_id,
            "get_list":m.get_list_of_nodes,
        },
        "properties": {
            "title": "Property",
            "list_title": "Properties",
            "template": "mdb-property.html",
            "subtype": "properties",
            "sort_key": lambda x: (x[1],x[2],x[3]),
            "display": "prop-tuple",
            "get_by_id": m.get_property_by_id,
            "get_list": m.get_list_of_properties,
        },
        "valuesets": {
            "title": "Value Set",
            "list_title": "Value Sets",
            "template": "mdb-valueset.html",
            "subtype": "valuesets",
            "sort_key": lambda x: x["handle"],
            "display": "list",
            "get_by_id": m.get_valueset_by_id,
            "get_list": m.get_list_of_valuesets,
        },
        "terms": {
            "title": "Term",
            "list_title": "Terms",
            "template": "mdb-term.html",
            "subtype": "terms",
            "sort_key": lambda x: (x["model"], x["property"], x["value"] if type(x["value"]) == str else ""),
            "display": "term-tuple",
            "get_by_id": m.get_term_by_id,
            "get_list": m.get_list_of_terms,
        },
        "origins": {
            "title": "Origin",
            "list_title": "Origins",
            "template": "mdb-origin.html",
            "subtype": "origins",
            "sort_key": lambda x:list(x.values())[0],
            "display": "list",
            "get_list": m.get_list_of_origins,
        },
    }

    # A: single entity
    if id is not None:
        ent_ = dispatch[entities]["get_by_id"](id)
        if ent_ is None or not bool(ent_):
            return render_template('/errors/400.html'), 400
        if ent_.get("has_properties"): # nodes only kludge
            ent_['has_properties'].sort(key=lambda x:x['handle'])
        if request.method == "GET":
            if format == "json":
                return jsonify(ent_)
            else:
                return render_template(
                    dispatch[entities]["template"],
                    title=dispatch[entities]["title"],
                    mdb=ent_,
                    subtype=dispatch[entities]["subtype"],
                    display="detail",
                )

    # B: filter by model
    ents_ = dispatch[entities]["get_list"]( None if model == 'All' else model)

    if format == "json":
        return jsonify(ents_)
    else:
        pagination = Pagination(page=page,total=len(ents_),record_name=entities)
        return render_template(
            "mdb.html",
            title=dispatch[entities]["list_title"],
            mdb=sorted(ents_,
                       key=dispatch[entities]["sort_key"]),
            subtype=dispatch[entities]["subtype"],
            display=dispatch[entities].get("display") or "tuple",
            first=(pagination.page-1)*pagination.per_page,
            last=min((pagination.page)*pagination.per_page,len(ents_)),
            pagination=pagination,
            form=select_form,
        )
# ---------------------------------------------------------------------------

@bp.route("/tags", defaults={'key':None,'value':None},methods=['GET','POST'])
@bp.route("/tags/<key>", methods=['GET','POST'], defaults={'value':None})
@bp.route("/tags/<key>/<value>", methods=['GET','POST'])
def tags(key=None,value=None,model=None):
    key = key or request.args.get("key")
    val = value or request.args.get("value")
    model = model or request.args.get("model")
    ents = []
    m = mdb()
    format = request.args.get("format")
    if request.form.get("format"):
        format = request.args.get("format")
    elif request.form.get("export"):
        format = "json"
    else:
        pass

    if key:
        ents = m.get_tagged_entities(key, val, model)
    else:
        ents = m.get_tags_and_values()

    if format == "json":
        return jsonify(ents)
    else:
        if key:
            return render_template(
                "mdb-tag.html",
                title="Tagged Entities",
                key=key,
                value=val,
                model=model,
                ents=ents,
                display='entities')
        else:
            return render_template(
                "mdb-tag.html",
                title="Tags",
                ents=ents,
                display='tags')

@bp.route("/search")
def search():

    if not g.search_form.validate():
        return redirect(url_for("main.index"))
    page = request.args.get("page", 1, type=int)

    hits, total = Entity.search(
        g.search_form.q.data, page, current_app.config["POSTS_PER_PAGE"]
    )
    next_url = (
        url_for("main.search", q=g.search_form.q.data, page=page + 1)
        if total > page * current_app.config["POSTS_PER_PAGE"]
        else None
    )
    prev_url = (
        url_for("main.search", q=g.search_form.q.data, page=page - 1)
        if page > 1
        else None
    )
    return render_template(
        "search.html",
        title="Search",
        hits=hits,
        next_url=next_url,
        prev_url=prev_url,
    )

@bp.route("/about-mdb")

def about_mdb():
    return render_template("about-mdb.html", title="About MDB")


@bp.route("/about-sts")

def about_sts():
    return render_template("about-sts.html", title="About STS")

@bp.errorhandler(413)
def too_large(e):
    return "File is too large", 413

@bp.route('/reports', methods=['GET', 'POST'])
def reports():
    return render_template('reports.html',)

@bp.route('/versionhistory', methods=['GET', 'POST'])
def versionhistory():
    return render_template('version-history.html')
