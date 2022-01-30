import os
from dotenv import load_dotenv
import yaml

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))
qp = yaml.load(
    open('/'.join([basedir,"query_paths.yml"]),"r"),
    Loader=yaml.CLoader
    )

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "supposedly-random-passphrase"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    NEO4J_MDB_URI = os.environ.get("NEO4J_MDB_URI")
    NEO4J_MDB_USER = os.environ.get("NEO4J_MDB_USER")
    NEO4J_MDB_PASS = os.environ.get("NEO4J_MDB_PASS")
    LANGUAGES = ["en"]
    MODEL_LIST = [] # set by MDB query in __init__
    MS_TRANSLATOR_KEY = os.environ.get("MS_TRANSLATOR_KEY")
    ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL")
    HITS_PER_PAGE = 25
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    JSONIFY_PRETTYPRINT_REGULAR = True
    SHOW_SINGLE_PAGE = True
    EDITING_FORMS = False
    QUERY_PATHS = qp
pass
