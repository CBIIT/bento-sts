import sys
from flask import render_template
from .errors import bp


@bp.app_errorhandler(401)
def bad_request_error(error):
    # db.session.rollback()
    return render_template("errors/400.html"), 401


@bp.app_errorhandler(404)
def not_found_error(error):
    print("WTH?", file=sys.stderr)
    return render_template("errors/404.html"), 404


@bp.app_errorhandler(500)
def internal_error(error):
#    db.session.rollback()
    return render_template("errors/500.html"), 500
