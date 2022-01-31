import sys
import re
from flask import (
    render_template,
    redirect,
    url_for,
    request,
    g,
    json,
    jsonify,
    current_app,
    Response,
    abort,
)
from werkzeug.exceptions import HTTPException
from app import logging
from app.mdb import mdb
from app.api import bp
sys.path.insert(0,"/Users/jensenma/Code/bento-meta/python")  # noqa E231

from bento_meta.util.makeq import Query

allowed_meths = ['GET', 'POST']

ents = {
    "model": "models",
    "node": "nodes",
    "prop": "props",
    "term": "terms",
    "edge": "edges",
    }

@bp.errorhandler(HTTPException)
def handle_exception(e):
    response = Response(
        status = e.code,
        response=json.dumps({
            "code": e.code,
            "description": str(e.description),
            })
        )
    response.content_type = "application/json"
    return response

@bp.before_app_request
def before_request():
    g.locale = 'EN_US'


@bp.route('/', methods=['GET'])
@bp.route('/v1', methods=['GET'])
def index():
    return jsonify({
        "application": "STS",
        "version": "0.1",
        "status": "READY"
    })


@bp.route("/v1/<path:path>", methods=allowed_meths)
def query_db(path):
    if not Query.paths:
        Query.set_paths(current_app.config["QUERY_PATHS"])
    current_app.logger.info(path)
    m = mdb()
    skip = request.args.get("skip")
    limit = request.args.get("limit")
    if not limit or limit > current_app.config['MAX_ENTS_PER_REQ']:
        limit = current_app.config['MAX_ENTS_PER_REQ'] 
    q = None
    total_rows = None
    try:
        q = Query(path)
    except Exception as e:
        abort(404, e)
    # look for a paired 'count'
    if not path.endswith('count'):
        try:
            qct = Query(path+"/count")
            ret = m.mdb.get_with_statement(str(qct), qct.params)
            total_rows = list(ret[0].values())[0]
        except Exception as e:
            current_app.logger.warn(e)
            pass
    
    stmt = str(q)
    if skip:
        stmt = stmt + " SKIP {}".format(int(skip))
    if limit:
        stmt = stmt + " LIMIT {}".format(int(limit))
    current_app.logger.info(stmt)
    ret = m.mdb.get_with_statement(stmt, q.params)
    if total_rows is not None:
        if total_rows > 0:
            ret.insert(0, {"total": total_rows})
        else:
            ret = {"total":0}
    return jsonify(ret)
