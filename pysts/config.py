import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


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
    MS_TRANSLATOR_KEY = os.environ.get("MS_TRANSLATOR_KEY")
    ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL")
    POSTS_PER_PAGE = 25
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    UPLOAD_EXTENSIONS = ['.yaml', '.yml']
    UPLOAD_PATH = 'uploads'
    DROPZONE_MAX_FILE_SIZE = 3
    DROPZONE_MAX_FILES = 30
    DROPZONE_ALLOWED_FILE_CUSTOM = True
    DROPZONE_ALLOWED_FILE_TYPE = 'text/*, .yml, .yaml'
    JSONIFY_PRETTYPRINT_REGULAR = True
    SHOW_SINGLE_PAGE = True
    EDITING_FORMS = False
    
pass
