import logging
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from bento_meta.mdb import MDB
from flask import Flask #, request, current_app
from flask_bootstrap import Bootstrap4
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect
from bento_sts.config import Config

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
    app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'spacelab'

    mdb = MDB(app.config["NEO4J_MDB_URI"],
              user=app.config["NEO4J_MDB_USER"],
              password=app.config["NEO4J_MDB_PASS"])
    app.config['MODEL_LIST'] = [x["m"] for x in mdb.get_model_nodes()]
    app.config['MODEL_LIST'].insert(0,{"handle":"All"})

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
            app.config['FLASK_LOGFILE'], maxBytes=10240, backupCount=10
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
        app.logger.info("STS startup")

    return app
