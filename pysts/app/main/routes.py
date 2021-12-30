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
from app.main.forms import SearchForm
# from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm, EditTermForm, DeprecateTermForm, DiffForm
# from app.main.forms import EditNodeForm, DeprecateNodeForm
# from app.main.forms import EditPropForm, DeprecatePropForm
import app.search
from app.main import bp
from app.util import get_yaml_for
import app.mdb
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
    m = app.mdb.mdb()

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

@bp.route("/nodes", defaults={'nodeid': None}, methods=['GET', 'POST'])
@bp.route('/nodes/<nodeid>', methods=['GET', 'POST'])

def nodes(nodeid):

    format = request.args.get("format")
    model = request.args.get("model")
    id_ = request.args.get("id")
    page = request.args.get(get_page_parameter(), type=int, default=1)

    id = nodeid
    if nodeid is None:
        if id_ is not None:
            id = id_

    current_app.logger.warn('> NODES id {} and id_{} and nodeid {}'.format(id, id_, nodeid))

    m = app.mdb.mdb()

    # A: single node
    if id is not None:
        node_ = m.get_node_by_id(id)
        # FIXME check that id actually exists - handle error

        if request.method == "GET":
            form.nodeHandle.data = node_['handle']

            if format == "json":
                return jsonify(node_)
            else:
                return render_template(
                    "mdb-node.html",
                    title="Node",
                    mdb=node_,
                    subtype="main.nodes",
                    display="detail",
                    form=form,
                    deprecateform=deprecateform,
                )

    # B: filter by model
    if model is not None:

        nodes_ = m.get_list_of_nodes(model)

        if format == "json":
            return jsonify(nodes_)
        else:
            pagination = Pagination(page=page,total=len(nodes_),record_name='nodes')
            return render_template(
                "mdb.html",
                title="Nodes in Model {}".format(model),
                mdb=sorted(nodes_,key=lambda x: x[1]),
                subtype="main.nodes",
                display="tuple",
                first=(pagination.page-1)*pagination.per_page,
                last=min((pagination.page)*pagination.per_page,len(nodes_)),
                pagination=pagination,
            )

    # C: plain list
    nodes_ = m.get_list_of_nodes()
    if format == "json":
        return jsonify(nodes_)
    else:
        pagination = Pagination(page=page,total=len(nodes_),record_name='nodes')
        return render_template(
            "mdb.html",
            title="Nodes",
            mdb=sorted(nodes_,key=lambda x:x[1]),
            subtype="main.nodes",
            display="tuple",  # from list
            first=(pagination.page-1)*pagination.per_page,
            last=min((pagination.page)*pagination.per_page,len(nodes_)),
            pagination=pagination,
        )


@bp.route("/properties", defaults={'propid': None}, methods=['GET', 'POST'])
@bp.route('/properties/<propid>', methods=['GET', 'POST'])

def properties(propid):

    format = request.args.get("format")  # for returning in json format
    model = request.args.get("model")    # to filter by model
    id_ = request.args.get("id")
    page = request.args.get(get_page_parameter(), type=int, default=1)
    
    id = propid
    if propid is None:
        if id_ is not None:
            id = id_

    current_app.logger.warn('> PROP id {} and id_{} and propid {}'.format(id, id_, propid ))

    m = app.mdb.mdb()

    # they specify property by id
    if id is not None:
        p_ = m.get_property_by_id(id, model)

        # FIX (not being hit)
        if p_ is None or not bool(p_):
            return render_template('/errors/400.html'), 400

        if format == "json":
            return jsonify(p_)
        else:
            return render_template(
                "mdb-property.html",
                title="Property: ",
                mdb=p_,
                subtype="main.properties",
                display="detail",
            )

    # they didn't give an id, so list all properties
    else:
        p_ = m.get_list_of_properties(model)
        if format == "json":
            return jsonify(p_)
        else:
            pagination = Pagination(page=page,total=len(p_),record_name='properties')
            return render_template(
                "mdb.html",
                title="Properties",
                mdb=sorted(p_, key=lambda x: (x[1],x[2],x[3])),
                subtype="main.properties",
                display="prop-tuple",  # from list
                first=(pagination.page-1)*pagination.per_page,
                last=min((pagination.page)*pagination.per_page,len(p_)),
                pagination=pagination,
            )


@bp.route("/valuesets", defaults={'valuesetid': None}, methods=['GET', 'POST'])
@bp.route('/valuesets/<valuesetid>', methods=['GET', 'POST'])

def valuesets(valuesetid):

    format = request.args.get("format")
    model = request.args.get("model")

    id_ = request.args.get("id")
    page = request.args.get(get_page_parameter(), type=int, default=1)
    id = valuesetid
    if valuesetid is None:
        if id_ is not None:
            id = id_

    current_app.logger.warn('> VS id {} and id_{} and valuesetid {}'.format(id, id_, valuesetid))

    m = app.mdb.mdb()

    if id is not None:
        vs_ = m.get_valueset_by_id(id, model)

        if vs_ is None or not bool(vs_):
            return render_template('/errors/400.html'), 400

        # TODO check that id actually exists - handle error
        if format == "json":
            return jsonify(vs_)
        else:
            return render_template(
                "mdb-valueset.html",
                title="Value Set: ",
                mdb=vs_,
                subtype="main.valuesets",
                display="detail",
            )

    else:
        vs_ = m.get_list_of_valuesets(model)
        pagination = Pagination(page=page,total=len(vs_),record_name='valuesets')
        if format == "json":
            return jsonify(vs_)
        else:
            return render_template(
                "mdb.html",
                title="Value Sets",
                mdb=sorted(vs_, key=lambda x: x["handle"]),
                subtype="main.valuesets",
                display="list",
                first=(pagination.page-1)*pagination.per_page,
                last=min((pagination.page)*pagination.per_page,len(vs_)),
                pagination=pagination,
            )


@bp.route("/terms", defaults={'termid': None}, methods=['GET', 'POST'])
@bp.route('/terms/<termid>', methods=['GET', 'POST'])

def terms(termid):

    format = request.args.get("format")
    model = request.args.get("model")    # to filter by model
    id_ = request.args.get("id")
    page = request.args.get(get_page_parameter(), type=int, default=1)
    
    id = termid
    if termid is None:
        if id_ is not None:
            id = id_

    current_app.logger.warn('> TERMS id {} and id_{} and termid {}'.format(id, id_, termid))

    m = app.mdb.mdb()

    if id is not None:
        term_ = m.get_term_by_id(id)
        if term_:
            if format == "json":
                return jsonify(term_)
            else:
                return render_template(
                    "mdb-term.html",
                    title="Term",
                    mdb=term_,
                    subtype="main.terms",
                    display="detail",
                )
    else:
        terms_ = m.get_list_of_terms(model)
        if format == "json":
            return jsonify(terms_)
        else:
            pagination = Pagination(page=page,total=len(terms_),record_name='terms')
            return render_template(
                "mdb.html",
                title="Terms",
                mdb=sorted(terms_,key=lambda x: (x["model"], x["property"], x["value"])),
                subtype="main.terms",
                display="term-tuple",
                first=(pagination.page-1)*pagination.per_page,
                last=min((pagination.page)*pagination.per_page,len(terms_)),
                pagination=pagination,
            )


@bp.route("/origins", defaults={'originid': None}, methods=['GET', 'POST'])
@bp.route('/origins/<originid>', methods=['GET', 'POST'])

def origins(originid):
    format = request.args.get("format")
    id_ = request.args.get("id")

    id = originid
    if originid is None:
        if id_ is not None:
            id = id_

    current_app.logger.warn('> ORIGIN id {} and id_{} and originid {}'.format(id, id_, originid))

    m = app.mdb.mdb()

    origins_ = m.get_list_of_origins()
    if format == "json":
        return jsonify(origins_)

    return render_template(
        "mdb.html",
        title="Origins",
        mdb=sorted(origins_,key=lambda x:list(x.values())[0]),
        subtype="main.origins",
        display="list",
        pagination=None,
        first=0,
        last=len(origins_)
    )


# ---------------------------------------------------------------------------
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
