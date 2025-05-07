import logging
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from flask import Flask  # , request, current_app
from flask_bootstrap import Bootstrap4
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect

from bento_sts.config import Config

from .mdb import mdb

bootstrap4 = Bootstrap4()
moment = Moment()
csrf = CSRFProtect()
load_dotenv(".env")
logger = logging.getLogger()


def create_app(config_class=Config):
    # see: "Application Object -> About the First Parameter"
    # at https://flask.palletsprojects.com/en/1.1.x/api/#flask.g
    app = Flask(__name__)
    app.config.from_object(config_class)

    """ or set to None for default theme """
    app.config["BOOTSTRAP_BOOTSWATCH_THEME"] = "spacelab"

    app.config["MDB"] = mdb(
        app.config["NEO4J_MDB_URI"],
        app.config["NEO4J_MDB_USER"],
        app.config["NEO4J_MDB_PASS"],
    )

    minfo = app.config["MDB"].mdb_.get_model_info()

    app.config["MODEL_LIST"] = sorted(set([x["handle"] for x in minfo]))
    app.config["VERSIONS_BY_MODEL"] = {
        m: sorted([v["version"] for v in minfo if v["handle"] == m])
        for m in app.config["MODEL_LIST"]
    }
    app.config["VERSIONS_BY_MODEL"] = {}
    app.config["LATEST_VERSION_BY_MODEL"] = {}
    # below assumes that minfo is sorted lexically by (model, version)
    for m in app.config["MODEL_LIST"]:
        for info in [x for x in minfo if x["handle"] == m]:
            if app.config["VERSIONS_BY_MODEL"].get(m):
                app.config["VERSIONS_BY_MODEL"][m].append(info["version"])
            else:
                app.config["VERSIONS_BY_MODEL"][m] = [info["version"]]
            if (
                info.get("latest_version") == True
                or info.get("is_latest_version") == True
            ):
                app.config["LATEST_VERSION_BY_MODEL"][m] = info["version"]
    for m in app.config["MODEL_LIST"]:
        if not app.config["LATEST_VERSION_BY_MODEL"].get(m):
            app.config["LATEST_VERSION_BY_MODEL"][m] = app.config["VERSIONS_BY_MODEL"][
                m
            ][0]

    app.config["MODEL_LIST"].insert(0, "ALL")

    bootstrap4.init_app(app)
    moment.init_app(app)
    csrf.init_app(app)

    from .main import bp as main_bp

    app.register_blueprint(main_bp)
    from .api import bp as api_bp

    app.register_blueprint(api_bp)
    from .errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    if not app.debug and not app.testing:
        file_handler = RotatingFileHandler(
            app.config["FLASK_LOGFILE"],
            maxBytes=10240,
            backupCount=10,
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]",
            ),
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.DEBUG)
        app.logger.info("STS startup")

    return app
