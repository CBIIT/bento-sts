"""Routes for the main STSapplication."""

import re
from importlib import metadata
from pathlib import Path

from flask import (
    Response,
    abort,
    current_app,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_paginate import Pagination, get_page_parameter

from . import bp
from .forms import (
    SearchForm,
    SelectModelForm,
    SelectVersionForm,
)

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def mdb():
    # only called in app context
    return current_app.config["MDB"]


def _get_package_version() -> str:
    """Get the current package version from metadata or source."""
    try:
        return metadata.version("bento-sts")
    except metadata.PackageNotFoundError:
        try:
            pyproject_path = (
                Path(__file__).parent.parent.parent.parent / "pyproject.toml"
            )
            with pyproject_path.open("rb") as f:
                pyproject_data = tomllib.load(f)
            return pyproject_data["project"]["version"]
        except Exception:
            return "Development"


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


@bp.route("/<entities>", defaults={"id": None}, methods=["GET", "POST"])
@bp.route("/<entities>/<id>", methods=["GET", "POST"])
@bp.route("/<entities>", defaults={"id": None}, methods=["GET", "POST"])
@bp.route("/<entities>/<id>", methods=["GET", "POST"])
def entities(entities, id):
    format = request.args.get("format") or request.form.get("format") or ""
    if request.form.get("export"):
        format = "json"

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
    dispatch = {
        "nodes": {
            "title": "Node",
            "list_title": "Nodes",
            "template": "mdb-node.html",
            "subtype": "nodes",
            "sort_key": lambda x: (x[1], x[2], x[3]),
            "get_by_id": mdb().get_node_by_id,
            "get_list": mdb().get_list_of_nodes,
        },
        "properties": {
            "title": "Property",
            "list_title": "Properties",
            "template": "mdb-property.html",
            "subtype": "properties",
            "sort_key": lambda x: (x["prop_handle"], x["node_model"], x["node_handle"]),
            "display": "prop-tuple",
            "get_by_id": mdb().get_property_by_id,
            "get_list": mdb().get_list_of_properties,
        },
        "valuesets": {
            "title": "Value Set",
            "list_title": "Value Sets",
            "template": "mdb-valueset.html",
            "subtype": "valuesets",
            "sort_key": lambda x: x["handle"],
            "display": "list",
            "get_by_id": mdb().get_valueset_by_id,
            "get_list": mdb().get_list_of_valuesets,
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
            "get_by_id": mdb().get_term_by_id,
            "get_list": mdb().get_list_of_terms,
        },
        "origins": {
            "title": "Origin",
            "list_title": "Origins",
            "template": "mdb-origin.html",
            "subtype": "origins",
            "sort_key": lambda x: list(x.values())[0],
            "display": "list",
            "get_list": mdb().get_list_of_origins,
            "get_by_id": mdb().get_origin_by_id,
        },
    }

    # Validate entity type before proceeding
    if entities not in dispatch:
        abort(404)

    # A: single entity
    if id is not None:
        ent_ = dispatch[entities]["get_by_id"](id)
        if ent_ is None or not bool(ent_):
            return render_template("/errors/400.html"), 400
        if type(ent_) == dict and ent_.get("has_properties"):  # nodes only kludge
            ent_["has_properties"].sort(key=lambda x: x["handle"])
        if format == "json":
            return jsonify(ent_)
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
        safe_model = re.escape(model)
        rendered = re.sub(
            f'option value="{safe_model}"',
            f'option selected="true" value={model}',
            rendered,
        )

    return rendered


# ---------------------------------------------------------------------------


@bp.route("/models", methods=["GET"])
@bp.route("/models/<name>", methods=["GET", "POST"])
def models(name=None):
    m = mdb()
    if name is not None:
        if name not in current_app.config["MODEL_LIST"]:
            return render_template("/errors/400.html"), 400
        version = (
            request.args.get("version")
            or request.form.get("version")
            or current_app.config["LATEST_VERSION_BY_MODEL"][name]
        )
        select_form = SelectVersionForm()
        select_form.version.choices = current_app.config["VERSIONS_BY_MODEL"][name]
        return render_template(
            "mdb-model.html",
            title=f"Model: {name}",
            name=name,
            version=version,
            mdb={
                "nodes": m.get_list_of_nodes(name, version),
                "props": m.get_list_of_properties(name, version),
            },
            subtype="main.models",
            display="detail",
            form=select_form,
        )

    models_ = m.get_list_of_models()
    return render_template(
        "mdb-model.html",
        title="Models",
        mdb=sorted(models_, key=lambda x: x["name"]),
        subtype="main.models",
        display="list",
    )


@bp.route("/terms", defaults={"start": 0}, methods=["GET", "POST"])
@bp.route("/terms/batch/<start>", methods=["GET", "POST"])
def terms(start, num=15):
    page = request.args.get(get_page_parameter(), type=int, default=1)
    (batches, tabnames) = mdb().get_term_batch_info(num)
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
            if batches[i]["first"] <= start <= batches[i]["last"]:
                activetab = i
                break
        (subbatches, subtabnames) = mdb().get_term_batch_info(
            num,
            batches[i]["first"],
            bsize,
        )
        for j in range(len(subbatches)):
            if subbatches[j]["first"] <= start < subbatches[j]["last"]:
                activesubtab = j
                break
        sbsize = subbatches[j]["last"] - subbatches[j]["first"] + 1
        batch = type(mdb()).get_term_batch(start, sbsize)
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
    format = request.args.get("format")
    if request.form.get("format"):
        format = request.args.get("format")
    elif request.form.get("export"):
        format = "json"
    else:
        pass

    if key:
        ents = mdb().get_tagged_entities(key, val)
    else:
        ents = mdb().get_tags_and_values()

    if format == "json":
        return jsonify(ents)
    if key:
        return render_template(
            "mdb-tag.html",
            title="Tagged Entities",
            key=key,
            value=val,
            ents=ents,
            display="entities",
        )
    return render_template("mdb-tag.html", title="Tags", ents=ents, display="tags")


@bp.route("/search")
def search():
    if not g.search_form.validate():
        return redirect(url_for("main.index"))
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
        ents = mdb().search_terms(qstring)
        thing = "terms"
    elif request.args.get("models"):
        ents = mdb().search_entity_handles(qstring)
        thing = "models"
    else:
        abort(400)
    if format == "json":
        return jsonify(ents)
    paging = {}
    pg_tot = 0
    activetab = "nodes"

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
        if len(ents["nodes"]) == 0:
            if len(ents["properties"]) > 0:
                activetab = "properties"
            elif len(ents["relationships"]) > 0:
                activetab = "relationships"
            else:
                thing = "no_hits"
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
        npr=["nodes", "properties", "relationships"],
        thing=thing,
        q=qstring,
        activetab=activetab,
        entdisplay=entdisplay,
        paging=paging,
    )


@bp.route("/about-mdb")
def about_mdb():
    return render_template("about-mdb.html", title="About MDB")


@bp.route("/about-sts")
def about_sts():
    return render_template("about-sts.html", title="About STS")


@bp.route("/favicon.ico")
def favicon():
    return send_from_directory("static", "favicon.ico")


@bp.errorhandler(413)
def too_large(e):
    return "File is too large", 413


@bp.route("/reports", methods=["GET", "POST"])
def reports():
    return render_template("reports.html")


@bp.route("/versionhistory", methods=["GET", "POST"])
def versionhistory():
    return render_template("version-history.html")


@bp.route(
    "/model-pvs/<model>/<version>",
    methods=["GET", "POST"],
    strict_slashes=False,
)
def cde_pvs_and_synonyms_by_model(model, version):
    """
    Get PVs and synonyms for a given model and version.

    Follows Data Hub logic for using PVs from CDE or model.
    """
    model = model or request.args.get("model") or request.form.get("model") or "ALL"
    version = (
        version or request.args.get("version") or request.form.get("version") or None
    )

    ents = []

    fmt = request.args.get("format")
    if request.form.get("format"):
        fmt = request.args.get("format")
    elif request.form.get("export"):
        fmt = "json"
    else:
        pass

    ents = type(mdb()).get_model_pvs_synonyms(model, version)

    if fmt == "json":
        # remove attrs other than values from props
        return jsonify(
            [{**item, "property": item["property"].get("handle", "")} for item in ents],
        )
    return render_template(
        "mdb-model-pvs.html",
        title="CDE Permissible Values and Synonyms by Model",
        ents=ents,
        display="cdes",
        model=model,
        version=version,
    )


@bp.route("/cde-pvs/<id>/<version>", methods=["GET", "POST"], strict_slashes=False)
@bp.route(
    "/cde-pvs/<id>",
    defaults={"version": None},
    methods=["GET", "POST"],
    strict_slashes=False,
)
def cde_pvs_by_id(id, version):
    """Get PVs for a given CDE id and optional version."""
    cde_id = id or request.args.get("id")
    cde_version = version or request.args.get("version") or ""
    ents = []

    fmt = request.args.get("format")
    if request.form.get("format"):
        fmt = request.args.get("format")
    elif request.form.get("export"):
        fmt = "json"
    else:
        pass

    ents = type(mdb()).get_cde_pvs_by_id(cde_id, cde_version)

    if fmt == "json":
        return jsonify(
            [
                {
                    "CDECode": item["cde"].get("origin_id", ""),
                    "CDEVersion": item["cde"].get("origin_version", ""),
                    "CDEFullName": item["cde"].get("value", ""),
                    "permissibleValues": item.get("permissibleValues", []),
                }
                for item in ents
            ],
        )
    return render_template(
        "mdb-cde-pvs.html",
        title="Common Data Element (CDE) Permissible Values",
        ents=ents,
        display="cde_pvs",
        id=cde_id,
        version=cde_version,
    )


@bp.route(
    "/term-by-origin/<origin_name>/<origin_id>",
    defaults={"origin_version": None},
    methods=["GET", "POST"],
    strict_slashes=False,
)
@bp.route(
    "/term-by-origin/<origin_name>/<origin_id>/<origin_version>",
    methods=["GET", "POST"],
    strict_slashes=False,
)
def term_by_origin(origin_name, origin_id, origin_version):
    """Get term by origin, origin_id, and origin_version."""
    origin_name = origin_name or request.args.get("origin_name")
    origin_id = origin_id or request.args.get("origin_id")
    origin_version = origin_version or request.args.get("origin_version") or ""

    term_nanoids = (
        type(mdb()).get_term_nanoid_by_origin(origin_name, origin_id, origin_version)
        or []
    )
    if term_nanoids:
        term_nanoid = term_nanoids[0]["term_nanoid"]
    if len(term_nanoids) > 1:
        msg = (
            f"More than one Term found for origin: {origin_name} "
            f"with id: {origin_id} and version: {origin_version}. "
            "Displaying first result only."
        )
        current_app.logger.warning(msg)

    return entities(entities="terms", id=term_nanoid)


@bp.route(
    "/all-pvs",
    methods=["GET", "POST"],
    strict_slashes=False,
)
def all_cde_pvs_and_synonyms():
    """
    Get all PVs and synonyms for a given model and version.

    Follows Data Hub logic for using PVs from CDE or model.
    """
    ents = []

    fmt = request.args.get("format")
    if request.form.get("format"):
        fmt = request.args.get("format")
    elif request.form.get("export"):
        fmt = "json"
    else:
        pass

    ents = type(mdb()).get_all_pvs_and_synonyms()

    if fmt == "json":
        # remove attrs other than values from props
        return jsonify(ents)
    return render_template(
        "mdb-all-pvs.html",
        title="CDE Permissible Values and Synonyms",
        ents=ents,
        display="cdes",
    )


# =============================================================================
# ADMIN ROUTES - Cache Management Tools
# =============================================================================


@bp.route("/admin/", methods=["GET"])
@bp.route("/admin/dashboard", methods=["GET"])
def admin_dashboard() -> str:
    """Admin dashboard with cache management tools."""
    package_version = _get_package_version()

    return render_template(
        "admin_dashboard.html",
        title="Admin Dashboard",
        package_version=package_version,
    )


@bp.route("/admin/clear-lru-caches", methods=["POST"])
def admin_clear_lru_caches() -> str:
    """Clear all LRU caches from the mdb class."""
    try:
        cleared_count = 0

        if hasattr(type(mdb()).get_term_batch, "cache_clear"):
            type(mdb()).get_term_batch.cache_clear()
            cleared_count += 1

        if hasattr(type(mdb()).get_model_pvs_synonyms, "cache_clear"):
            type(mdb()).get_model_pvs_synonyms.cache_clear()
            cleared_count += 1

        if hasattr(type(mdb()).get_cde_pvs_by_id, "cache_clear"):
            type(mdb()).get_cde_pvs_by_id.cache_clear()
            cleared_count += 1

        if hasattr(type(mdb()).get_term_nanoid_by_origin, "cache_clear"):
            type(mdb()).get_term_nanoid_by_origin.cache_clear()
            cleared_count += 1

        if hasattr(type(mdb()).get_cde_pvs_and_synonyms_by_id, "cache_clear"):
            type(mdb()).get_cde_pvs_and_synonyms_by_id.cache_clear()
            cleared_count += 1

        if hasattr(type(mdb()).get_all_pvs_and_synonyms, "cache_clear"):
            type(mdb()).get_all_pvs_and_synonyms.cache_clear()
            cleared_count += 1

        flash(f"Cleared {cleared_count} LRU caches successfully.", "success")

    except Exception as e:
        current_app.logger.exception("Error clearing LRU caches")
        flash(f"Error clearing LRU caches: {e!s}", "error")

    return redirect(url_for("main.admin_dashboard"))


@bp.route("/admin/refresh-mdb", methods=["POST"])
def admin_refresh_mdb() -> str:
    """Refresh the MDB/SearchableMDB instance."""
    try:
        if (
            current_app.config["MDB"]
            and hasattr(current_app.config["MDB"], "mdb_")
            and current_app.config["MDB"].mdb_
        ):
            current_app.config["MDB"].mdb_.close()

        type(mdb()).mdb_ = None

        current_app.config["MDB"] = type(mdb())(
            current_app.config["NEO4J_MDB_URI"],
            current_app.config["NEO4J_MDB_USER"],
            current_app.config["NEO4J_MDB_PASS"],
        )

        flash(
            "MDB instance refreshed successfully (includes search indexes).",
            "success",
        )

    except Exception as e:
        current_app.logger.exception("Error refreshing MDB")
        flash(f"Error refreshing MDB: {e!s}", "error")

    return redirect(url_for("main.admin_dashboard"))


@bp.route("/admin/refresh-model-lists", methods=["POST"])
def admin_refresh_model_lists() -> str:
    """Regenerate model lists from MDB."""
    try:
        type(mdb()).term_values = None

        minfo = current_app.config["MDB"].mdb_.get_model_info()

        current_app.config["MODEL_LIST"] = sorted({x["handle"] for x in minfo})
        current_app.config["VERSIONS_BY_MODEL"] = {}
        current_app.config["LATEST_VERSION_BY_MODEL"] = {}

        # Rebuild version mappings
        for m in current_app.config["MODEL_LIST"]:
            for info in [x for x in minfo if x["handle"] == m]:
                if current_app.config["VERSIONS_BY_MODEL"].get(m):
                    current_app.config["VERSIONS_BY_MODEL"][m].append(info["version"])
                else:
                    current_app.config["VERSIONS_BY_MODEL"][m] = [info["version"]]
                if (
                    info.get("latest_version") == True
                    or info.get("is_latest_version") == True
                ):
                    current_app.config["LATEST_VERSION_BY_MODEL"][m] = info["version"]

        for m in current_app.config["MODEL_LIST"]:
            if not current_app.config["LATEST_VERSION_BY_MODEL"].get(m):
                current_app.config["LATEST_VERSION_BY_MODEL"][m] = current_app.config[
                    "VERSIONS_BY_MODEL"
                ][m][0]

        if "ALL" not in current_app.config["MODEL_LIST"]:
            current_app.config["MODEL_LIST"].insert(0, "ALL")

        model_count = len(current_app.config["MODEL_LIST"]) - 1
        flash(
            f"Model lists refreshed successfully ({model_count} models found).",
            "success",
        )

    except Exception as e:
        current_app.logger.exception("Error refreshing model lists")
        flash(f"Error refreshing model lists: {e!s}", "error")

    return redirect(url_for("main.admin_dashboard"))


@bp.route("/admin/clear-all-caches", methods=["POST"])
def admin_clear_all_caches():
    """Clear all caches: LRU caches, refresh MDB, and regenerate model lists."""
    try:
        cleared_lru = 0
        if hasattr(type(mdb()).get_term_batch, "cache_clear"):
            type(mdb()).get_term_batch.cache_clear()
            cleared_lru += 1
        if hasattr(type(mdb()).get_model_pvs_synonyms, "cache_clear"):
            type(mdb()).get_model_pvs_synonyms.cache_clear()
            cleared_lru += 1
        if hasattr(type(mdb()).get_cde_pvs_by_id, "cache_clear"):
            type(mdb()).get_cde_pvs_by_id.cache_clear()
            cleared_lru += 1
        if hasattr(type(mdb()).get_term_nanoid_by_origin, "cache_clear"):
            type(mdb()).get_term_nanoid_by_origin.cache_clear()
            cleared_lru += 1
        if hasattr(type(mdb()).get_cde_pvs_and_synonyms_by_id, "cache_clear"):
            type(mdb()).get_cde_pvs_and_synonyms_by_id.cache_clear()
            cleared_lru += 1
        if hasattr(type(mdb()).get_all_pvs_and_synonyms, "cache_clear"):
            type(mdb()).get_all_pvs_and_synonyms.cache_clear()
            cleared_lru += 1

        type(mdb()).term_values = None

        if current_app.config["MDB"] and hasattr(current_app.config["MDB"], "mdb_"):
            if current_app.config["MDB"].mdb_ and hasattr(
                current_app.config["MDB"].mdb_,
                "close",
            ):
                current_app.config["MDB"].mdb_.close()

        type(mdb()).mdb_ = None
        current_app.config["MDB"] = type(mdb())(
            current_app.config["NEO4J_MDB_URI"],
            current_app.config["NEO4J_MDB_USER"],
            current_app.config["NEO4J_MDB_PASS"],
        )

        minfo = current_app.config["MDB"].mdb_.get_model_info()
        current_app.config["MODEL_LIST"] = sorted({x["handle"] for x in minfo})
        current_app.config["VERSIONS_BY_MODEL"] = {}
        current_app.config["LATEST_VERSION_BY_MODEL"] = {}

        for m in current_app.config["MODEL_LIST"]:
            for info in [x for x in minfo if x["handle"] == m]:
                if current_app.config["VERSIONS_BY_MODEL"].get(m):
                    current_app.config["VERSIONS_BY_MODEL"][m].append(info["version"])
                else:
                    current_app.config["VERSIONS_BY_MODEL"][m] = [info["version"]]
                if (
                    info.get("latest_version") == True
                    or info.get("is_latest_version") == True
                ):
                    current_app.config["LATEST_VERSION_BY_MODEL"][m] = info["version"]

        for m in current_app.config["MODEL_LIST"]:
            if not current_app.config["LATEST_VERSION_BY_MODEL"].get(m):
                current_app.config["LATEST_VERSION_BY_MODEL"][m] = current_app.config[
                    "VERSIONS_BY_MODEL"
                ][m][0]

        if "ALL" not in current_app.config["MODEL_LIST"]:
            current_app.config["MODEL_LIST"].insert(0, "ALL")

        model_count = len(current_app.config["MODEL_LIST"]) - 1
        flash(
            f"All caches cleared successfully! Refreshed {cleared_lru} LRU caches, "
            f"MDB instance (with indexes), and {model_count} models.",
            "success",
        )

    except Exception as e:
        current_app.logger.exception("Error clearing all caches")
        flash(f"Error clearing all caches: {e!s}", "error")

    return redirect(url_for("main.admin_dashboard"))


@bp.route("/admin/indexes", methods=["GET"])
def admin_list_indexes():
    """Compare cached vs current Neo4j indexes to test refresh behavior."""
    try:
        cached_indexes = mdb().mdb.available_indexes()

        show_indexes_stmt = (
            "SHOW INDEXES YIELD name, state, type, labelsOrTypes, properties "
            "RETURN name, state, type, labelsOrTypes, properties"
        )
        current_indexes = mdb().get_with_statement(show_indexes_stmt, {})

        current_fulltext = {
            idx["name"]: {
                "state": idx.get("state", "unknown"),
                "entity_type": idx.get("labelsOrTypes", []),
                "properties": idx.get("properties", []),
            }
            for idx in current_indexes
            if idx.get("type") == "FULLTEXT"
        }

        comparison = {}
        all_index_names = set(cached_indexes.keys()) | set(current_fulltext.keys())

        for index_name in all_index_names:
            in_cache = index_name in cached_indexes
            in_db = index_name in current_fulltext

            if in_cache and in_db:
                comparison[index_name] = {
                    "status": "✅ Cached and Available",
                    "cached": cached_indexes[index_name],
                    "current": current_fulltext[index_name],
                }
            elif in_cache and not in_db:
                comparison[index_name] = {
                    "status": "⚠️ Cached but Missing from DB",
                    "cached": cached_indexes[index_name],
                    "current": None,
                }
            elif not in_cache and in_db:
                comparison[index_name] = {
                    "status": "🔄 Available but Not Cached (needs refresh)",
                    "cached": None,
                    "current": current_fulltext[index_name],
                }

        needs_refresh = any(
            status["status"].startswith("⚠️") or status["status"].startswith("🔄")
            for status in comparison.values()
        )

        return jsonify(
            {
                "cached_indexes": cached_indexes,
                "current_fulltext_indexes": current_fulltext,
                "comparison": comparison,
                "needs_refresh": needs_refresh,
                "all_indexes": current_indexes,  # Keep for debugging
                "status": "success",
            },
        )

    except Exception as e:
        current_app.logger.exception("Error listing indexes")
        flash(f"Error listing indexes: {e!s}", "error")
        return redirect(url_for("main.admin_dashboard"))


@bp.route("/admin/version", methods=["GET"])
def admin_version_info() -> Response:
    """Return version information as JSON."""
    package_version = _get_package_version()

    return jsonify(
        {
            "package": "bento-sts",
            "version": package_version,
            "status": "running",
        },
    )
