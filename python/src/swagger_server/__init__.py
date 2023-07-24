import connexion
from . import encoder
from importlib_resources import files

def create_app():
    app = connexion.App(__name__, specification_dir=files().joinpath('swagger'))
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api(files().joinpath('swagger/swagger.yaml'), arguments={'title': 'Simple Terminology Server API'})
    return app.app  # this returns a Flask app corresponding to the Connexion app
