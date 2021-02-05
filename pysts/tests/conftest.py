import pytest
from config import Config
from app import create_app
import requests
from requests.exceptions import ConnectionError
from time import sleep

wait = 15


@pytest.fixture
def app():
    app = create_app()
    return app


# @pytest.fixture(scope='module')
# def test_client():
#    #flask_app = create_app('flask_test.cfg')
#    flask_app = create_app(config_class=Config)
#
#    # Create a test client using the Flask application configured for testing
#    with flask_app.client() as testing_client:
#        # Establish an application context
#        with flask_app.app_context():
#            yield testing_client  # this is where the testing happens!

# @pytest.fixture
# def app():
#    yield create_app
#
#
# @pytest.fixture
# def client(app):
#    return app.test_client()


def is_responsive(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False


@pytest.fixture(scope="session")
def docker_bento_neo4j(docker_services, docker_ip):
    bolt_port = docker_services.port_for("bento-neo4j", 7687)
    http_port = docker_services.port_for("bento-neo4j", 7474)
    bolt_url = "bolt://{}:{}".format(docker_ip, bolt_port)
    http_url = "http://{}:{}".format(docker_ip, http_port)
    sleep(wait)
    docker_services.wait_until_responsive(
        timeout=5.0, pause=1.0, check=lambda: is_responsive(http_url)
    )
    return bolt_url


@pytest.fixture(scope="session")
def docker_plain_neo4j(docker_services, docker_ip):
    bolt_port = docker_services.port_for("plain-neo4j", 7687)
    http_port = docker_services.port_for("plain-neo4j", 7474)
    bolt_url = "bolt://{}:{}".format(docker_ip, bolt_port)
    http_url = "http://{}:{}".format(docker_ip, http_port)
    sleep(wait)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.5, check=lambda: is_responsive(http_url)
    )
    return (bolt_url, http_url)
