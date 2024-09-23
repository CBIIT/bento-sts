import pytest
import string
from bento_sts.config import Config
from bento_sts.sts import create_app


@pytest.fixture
def app():
    app = create_app()
    return app


@pytest.fixture()
def test_paths(model="ICDC", version="1.0", handle="diagnosis",
               phandle="disease_term", key="Class", value="primary", nanoid="abF32k"):
    tpl = [
        "/models",
        "/models/count",
        "/model/$model/version/$version/nodes",
        "/model/$model/version/$version/nodes/count",
        "/model/$model/version/$version/node/$handle",
        "/model/$model/version/$version/node/$handle/properties",
        "/model/$model/version/$version/node/$handle/properties/count",
        "/model/$model/version/$version/node/$handle/property/$phandle",
        "/model/$model/version/$version/node/$handle/property/$phandle/terms",
        "/model/$model/version/$version/node/$handle/property/$phandle/terms/count",
        "/model/$model/version/$version/node/$handle/property/$phandle/term/$value",
        "/tags",
        "/tags/count",
        "/tag/$key/values",
        "/tag/$key/values/count",
        "/tag/$key/$value/entities",
        "/tag/$key/$value/entities/count",
        "/term/$value",
        "/term/$value/count",
        "/id/$nanoid"
        ]
    return [string.Template(x).
            safe_substitute(model=model, version=version, handle=handle, phandle=phandle,
                            key=key, value=value, nanoid=nanoid) for x in tpl]


#@pytest.fixture(scope='module')
#def test_client():
#    #flask_app = create_app('flask_test.cfg')
#    flask_app = create_app(config_class=Config)
#
#    # Create a test client using the Flask application configured for testing
#    with flask_app.client() as testing_client:
#        # Establish an application context
#        with flask_app.app_context():
#            yield testing_client  # this is where the testing happens!

#@pytest.fixture
#def app():
#    yield create_app
#
#
#@pytest.fixture
#def client(app):
#    return app.test_client()
