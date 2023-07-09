import sys
print("main routes", file=sys.stderr)
import re
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
)
from flask_paginate import Pagination, get_page_parameter
from .forms import SearchForm, SelectModelForm
# import app.search
from . import bp
from ..util import get_yaml_for
from ..mdb import mdb
# from app.arc import diff_mdf



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

@bp.route("/<entities>", defaults={'id': None}, methods=['GET','POST'])
@bp.route('/<entities>/<id>', methods=['GET','POST'])

def entities(entities, id):

    if request.form.get("format"):
        format = request.args.get("format")
    elif request.form.get("export"):
        format = "json"
    else:
        format = ""

    model = request.args.get("model") or request.form.get("model") or "All"
    id_ = request.args.get("id")
    page = request.args.get(get_page_parameter(), type=int, default=1)
    select_form = SelectModelForm()
    select_form.model.choices = [(x['handle'],x['handle']) for x
                                     in current_app.config["MODEL_LIST"]]
    current_app.logger.info("model: {}, page: {}, format: {}".format(model, page, format))
    id = id or id_
    m = mdb()
    dispatch = {
        "nodes": {
            "title": "Node",
            "list_title": "Nodes",
            "template": "mdb-node.html",
            "subtype": "nodes",
            "sort_key": lambda x: x[1],
            "get_by_id": m.get_node_by_id,
            "get_list":m.get_list_of_nodes,
        },
        "properties": {
            "title": "Property",
            "list_title": "Properties",
            "template": "mdb-property.html",
            "subtype": "properties",
            "sort_key": lambda x: (x[1], x[2], x[3]),
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
            "get_by_id": m.get_origin_by_id
        },
    }

    # A: single entity
    if id is not None:
        ent_ = dispatch[entities]["get_by_id"](id)
        if ent_ is None or not bool(ent_):
            return render_template('/errors/400.html'), 400
        if type(ent_) == dict and ent_.get("has_properties"): # nodes only kludge
            ent_['has_properties'].sort(key=lambda x:x['handle'])
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
        pgurl = url_for('main.entities',entities=entities)
        pgurl += "?page={0}"
        if model:
            pgurl += "&model={}".format(model)
        pagination = Pagination(
            page=page,
            total=len(ents_),
            record_name=entities,
            href=pgurl
            )
        rendered = render_template(
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
            model=model
        )
        # get a load of THIS kludge, dude.
        if model:
            rendered = re.sub('option value="{}"'.format(model),
                            'option selected="true" value={}'.format(model),
                            rendered)

        return rendered
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
    m = mdb()
    format = request.args.get("format")
    if request.form.get("format"):
        format = request.args.get("format")
    elif request.form.get("export"):
        format = "json"
    else:
        pass

    qstring = request.args.get("qstring")
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
    if format == 'json':
        return jsonify(ents)

    pg_tot = 0
    if thing == "terms":
        pg_tot = len(ents)
    elif thing == "models":
        pg_tot = max(len(ents["nodes"]), len(ents["properties"]),
                     len(ents["relationships"]))
    else:
        pass
    pagination = Pagination(
        page=request.args.get("page", 1, type=int),
        record_name="Hits",
        total=pg_tot,
        per_page=current_app.config["HITS_PER_PAGE"],
        )
    first = {}
    last = {}
    nohits = False
    if thing == "terms":
        if ents:
            first["terms"] = (pagination.page-1)*pagination.per_page
            last["terms"] = min(pagination.page*pagination.per_page, len(ents))
        else:
            thing = "no_hits"
    elif thing == "models":
        if ents:
            pp = round(pagination.per_page/3)
            first["nodes"] = min(len(ents["nodes"])-pp,
                                 pagination.page-1*pp)
            last["nodes"] = min(len(ents["nodes"]),
                                pagination.page*pp)
            first["properties"] = min(len(ents["properties"])-pp,
                                      pagination.page-1*pp)
            last["properties"] = min(len(ents["properties"]),
                                     pagination.page*pp)
            first["relationships"] = min(len(ents["relationships"])-pp,
                                         pagination.page-1*pp)
            last["relationships"] = min(len(ents["relationships"]),
                                        pagination.page*pp)
        else:
            thing = "no_hits"
    else:
        raise RuntimeError("Huh???")
    
    return render_template(
        "search.html",
        title="Search",
        ents=ents,
        thing=thing,
        pagination=pagination,
        first=first,
        last=last,
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
