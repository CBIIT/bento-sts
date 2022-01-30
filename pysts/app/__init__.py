import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from bento_meta.mdb import MDB
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_dropzone import Dropzone
from flask_wtf.csrf import CSRFProtect
import flask_excel
from elasticsearch import Elasticsearch
from config import Config

db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
moment = Moment()
csrf = CSRFProtect()


def create_app(config_class=Config):
    # see: "Application Object -> About the First Parameter"
    # at https://flask.palletsprojects.com/en/1.1.x/api/#flask.g
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_class)

    """ or set to None for default theme """
    app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'spacelab' 

    mdb = MDB(app.config["NEO4J_MDB_URI"],
              user=app.config["NEO4J_MDB_USER"],
              password=app.config["NEO4J_MDB_PASS"])
    app.config['MODEL_LIST'] = [x["m"] for x in mdb.get_model_nodes()]

    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    moment.init_app(app)
    csrf.init_app(app)
    flask_excel.init_excel(app)
    app.elasticsearch = (
        Elasticsearch([app.config["ELASTICSEARCH_URL"]])
        if app.config["ELASTICSEARCH_URL"]
        else None
    )

    # from app.errors import bp as errors_bp
    # app.register_blueprint(errors_bp)

    # from app.main import bp as main_bp
    # app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)
    
    if not app.debug and not app.testing:
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/pysts.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s"
                " [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.DEBUG)
        app.logger.info("pySTS startup")

    return app

