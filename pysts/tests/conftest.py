import pytest
from config import Config
from app import create_app


@pytest.fixture
def app():
    app = create_app()
    return app


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
