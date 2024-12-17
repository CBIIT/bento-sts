import re

from flask import (
    abort,
    current_app,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_paginate import Pagination, get_page_parameter

from bento_sts.mdb import mdb

from . import bp
from .forms import SearchForm, SelectModelForm, SelectVersionForm


@bp.before_app_request
def before_request():
    g.search_form = SearchForm()
    g.locale = "EN_US"


@bp.route("/", methods=["GET", "POST"])
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
    # format = request.args.get("format")
    m = mdb()

    if name is not None:
        models_ = m.get_model_by_name(name)  # list of versions of model <name>
        select_form = SelectVersionForm()
        select_form.version.choices = current_app.config["VERSIONS_BY_MODEL"][name]
        return render_template(
            "mdb-model.html",
            title=f"Model: {models_[0].handle}",
            mdb=models_,
            subtype="main.models",
            display="detail",
            form=select_form,
        )

    else:
        models_ = m.get_list_of_models()
        return render_template(
            "mdb-model.html",
            title="Models",
            mdb=sorted(models_, key=lambda x: x["name"]),
            subtype="main.models",
            display="list",
        )


@bp.route("/<entities>", defaults={"id": None}, methods=["GET", "POST"])
@bp.route("/<entities>/<id>", methods=["GET", "POST"])
def entities(entities, id):
    if request.form.get("format"):
        format = request.args.get("format")
    elif request.form.get("export"):
        format = "json"
    else:
        format = ""

    model = request.args.get("model") or request.form.get("model") or "ALL"
    version = request.args.get("version") or request.form.get("version") or None
    id_ = request.args.get("id")
    page = request.args.get(get_page_parameter(), type=int, default=1)
    select_form = SelectModelForm()
    select_form.model.choices = [(x, x) for x in current_app.config["MODEL_LIST"]]
    if model != "ALL":
        select_form.version.choices = [
            (x, x) for x in current_app.config["VERSIONS_BY_MODEL"][model]
        ]
        select_form.version.choices.insert(0, ("ALL", "ALL"))
    else:
        select_form.version.choices = [("ALL", "ALL")]
        version = "*"

    current_app.logger.info(
        f"model: {model}, version: {version}, page: {page}, format: {format}",
    )
    id = id or id_
    m = mdb()
    dispatch = {
        "nodes": {
            "title": "Node",
            "list_title": "Nodes",
            "template": "mdb-node.html",
            "subtype": "nodes",
            "sort_key": lambda x: (x[1], x[2], x[3]),
            "get_by_id": m.get_node_by_id,
            "get_list": m.get_list_of_nodes,
        },
        "properties": {
            "title": "Property",
            "list_title": "Properties",
            "template": "mdb-property.html",
            "subtype": "properties",
            "sort_key": lambda x: (x["prop_handle"], x["node_model"], x["node_handle"]),
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
            "sort_key": lambda x: (
                x["value"].lower() if type(x["value"]) == str else ""
            ),
            "display": "term-tuple",
            "get_by_id": m.get_term_by_id,
            "get_list": m.get_list_of_terms,
        },
        "origins": {
            "title": "Origin",
            "list_title": "Origins",
            "template": "mdb-origin.html",
            "subtype": "origins",
            "sort_key": lambda x: list(x.values())[0],
            "display": "list",
            "get_list": m.get_list_of_origins,
            "get_by_id": m.get_origin_by_id,
        },
    }

    # A: single entity
    if id is not None:
        ent_ = dispatch[entities]["get_by_id"](id)
        if ent_ is None or not bool(ent_):
            return render_template("/errors/400.html"), 400
        if type(ent_) == dict and ent_.get("has_properties"):  # nodes only kludge
            ent_["has_properties"].sort(key=lambda x: x["handle"])
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

    # B: list, filter by model
    get_list_args = (model, version)
    if entities in ["origins", "terms"]:
        get_list_args = ()
    ents_ = dispatch[entities]["get_list"](*get_list_args)

    if format == "json":
        return jsonify(ents_)
    else:
        pgurl = url_for("main.entities", entities=entities)
        pgurl += "?page={0}"
        if model:
            pgurl += f"&model={model}"
        pagination = Pagination(
            page=page,
            total=len(ents_),
            record_name=entities,
            href=pgurl,
        )
        rendered = render_template(
            "mdb.html",
            title=dispatch[entities]["list_title"],
            mdb=sorted(ents_, key=dispatch[entities]["sort_key"]),
            subtype=dispatch[entities]["subtype"],
            display=dispatch[entities].get("display") or "tuple",
            first=(pagination.page - 1) * pagination.per_page,
            last=min((pagination.page) * pagination.per_page, len(ents_)),
            pagination=pagination,
            form=select_form,
            model=model,
        )
        # get a load of THIS kludge, dude.
        if model:
            rendered = re.sub(
                f'option value="{model}"',
                f'option selected="true" value={model}',
                rendered,
            )

        return rendered


# ---------------------------------------------------------------------------


@bp.route("/terms", defaults={"start": 0}, methods=["GET", "POST"])
@bp.route("/terms/batch/<start>", methods=["GET", "POST"])
def terms(start, num=15):
    page = request.args.get(get_page_parameter(), type=int, default=1)
    m = mdb()
    (batches, tabnames) = m.get_term_batch_info(num)
    activetab = -1
    activesubtab = -1
    subbatches = None
    subtabnames = None
    batch = None
    paging = {}
    if start is not None:
        start = int(start)
        bsize = batches[0]["last"] - batches[0]["first"] + 1
        for i in range(len(batches)):
            if batches[i]["first"] <= start and start <= batches[i]["last"]:
                activetab = i
                break
        (subbatches, subtabnames) = m.get_term_batch_info(
            num,
            batches[i]["first"],
            bsize,
        )
        for j in range(len(subbatches)):
            if subbatches[j]["first"] <= start and start < subbatches[j]["last"]:
                activesubtab = j
                break
        sbsize = subbatches[j]["last"] - subbatches[j]["first"] + 1
        batch = mdb.get_term_batch(start, sbsize)
        pgurl = url_for("main.terms", start=start)
        pgurl += "?page={0}"
        pagination = Pagination(
            page=page,
            total=len(batch),
            record_name=entities,
            href=pgurl,
        )
        paging["pagination"] = pagination
        paging["first"] = (pagination.page - 1) * pagination.per_page
        paging["last"] = min((pagination.page) * pagination.per_page, len(batch))

    return render_template(
        "mdb-term-tabs.html",
        title="Terms",
        tabnames=tabnames,
        subtabnames=subtabnames,
        batches=batches,
        subbatches=subbatches,
        activetab=activetab,
        activesubtab=activesubtab,
        batch=batch,
        paging=paging,
    )


@bp.route("/tags", defaults={"key": None, "value": None}, methods=["GET", "POST"])
@bp.route("/tags/<key>", methods=["GET", "POST"], defaults={"value": None})
@bp.route("/tags/<key>/<value>", methods=["GET", "POST"])
def tags(key=None, value=None, model=None):
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
        ents = m.get_tagged_entities(key, val)
    else:
        ents = m.get_tags_and_values()

    if format == "json":
        return jsonify(ents)
    elif key:
        return render_template(
            "mdb-tag.html",
            title="Tagged Entities",
            key=key,
            value=val,
            ents=ents,
            display="entities",
        )
    else:
        return render_template("mdb-tag.html", title="Tags", ents=ents, display="tags")


@bp.route("/search")
def search():
    if not g.search_form.validate():
        return redirect(url_for("main.index"))
    m = mdb()
    format = request.args.get("format")
    if request.form.get("format"):
        format = request.args.get("format")
    elif request.form.get("export"):
        format = "json"
    else:
        pass

    qstring = request.args.get("qstring")
    entdisplay = request.args.get("entdisplay") or "nodes"
    ents = []
    thing = ""
    if request.args.get("terms"):
        ents = m.search_terms(qstring)
        thing = "terms"
    elif request.args.get("models"):
        ents = m.search_entity_handles(qstring)
        thing = "models"
    else:
        abort(400)
    if format == "json":
        return jsonify(ents)
    paging = {}
    pg_tot = 0
    if not ents:
        thing = "no_hits"
    if thing == "terms":
        pg_tot = len(ents)
        pagination = Pagination(
            page=request.args.get("page", 1, type=int),
            record_name="Hits",
            total=pg_tot,
            per_page=current_app.config["HITS_PER_PAGE"],
        )
        paging["terms"] = {"pagination": pagination}
        paging["terms"]["first"] = (pagination.page - 1) * pagination.per_page
        paging["terms"]["last"] = min(pagination.page * pagination.per_page, len(ents))
        entdisplay = "terms"
    elif thing == "models":
        paging = None
        # for ent in ("nodes", "properties", "relationships"):
        #     pagination = Pagination(
        #         page=request.args.get("page",1,type=int),
        #         record_name="Hits",
        #         total=len(ents[ent]),
        #         anchor=ent,
        #         per_page=current_app.config["HITS_PER_PAGE"],
        #     )
        #     paging[ent] = {"pagination": pagination}
        #     paging[ent]['first'] = (pagination.page-1)*pagination.per_page
        #     paging[ent]['last'] = min(pagination.page*pagination.per_page,len(ents[ent]))

    return render_template(
        "search.html",
        title="Search",
        ents=ents,
        thing=thing,
        q=qstring,
        entdisplay=entdisplay,
        paging=paging,
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


@bp.route("/reports", methods=["GET", "POST"])
def reports():
    return render_template("reports.html")


@bp.route("/versionhistory", methods=["GET", "POST"])
def versionhistory():
    return render_template("version-history.html")


# @bp.route("/cdes", defaults={"model": None, "version": None}, methods=["GET", "POST"])
# @bp.route("/cdes/<model>", methods=["GET", "POST"], defaults={"version": None})
@bp.route("/cdes/<model>/<version>", methods=["GET", "POST"])
def cde_pvs_and_synonyms(model, version):
    """Get CDE PVs and synonyms for a given model and version."""
    model = model or request.args.get("model")
    version = version or request.args.get("version")
    ents = []
    mdb()  # instantiate so mdb.mdb_ is available for get_cde_pvs

    fmt = request.args.get("format")
    if request.form.get("format"):
        fmt = request.args.get("format")
    elif request.form.get("export"):
        fmt = "json"
    else:
        pass

    ents = mdb.get_cde_pvs(model, version)

    if fmt == "json":
        # remove attrs other than values from props
        return jsonify(
            [{**item, "property": item["property"].get("handle", "")} for item in ents],
        )
    return render_template(
        "mdb-cdes.html",
        title="CDE Permissible Values and Synonyms",
        ents=ents,
        display="cdes",
        model=model,
        version=version,
    )
