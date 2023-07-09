import os
from bento_sts import config_sts
import yaml
from importlib_resources import files

src = files(config_sts).joinpath("query_paths.yml")
with src.open('r') as fh:
    qp = yaml.load(fh, Loader=yaml.CLoader)

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "supposedly-random-passphrase"
    NEO4J_MDB_URI = os.environ.get("NEO4J_MDB_URI")
    NEO4J_MDB_USER = os.environ.get("NEO4J_MDB_USER")
    NEO4J_MDB_PASS = os.environ.get("NEO4J_MDB_PASS")
    FLASK_LOGFILE = os.environ.get("STS_LOGFILE") or "sts.log"
    LANGUAGES = ["en"]
    MODEL_LIST = [] # set by MDB query in sts.py
    HITS_PER_PAGE = 25
    MAX_ENTS_PER_REQ = 500
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    JSONIFY_PRETTYPRINT_REGULAR = True
    SHOW_SINGLE_PAGE = True
    EDITING_FORMS = False
    QUERY_PATHS = qp
    WTF_CSRF_CHECK_DEFAULT = False

