import pytest
import requests
import string
import os
from requests.exceptions import ConnectionError
from time import sleep
from bento_sts.sts import create_app
from bento_sts.config import Config
from pdb import set_trace

wait = 10
timeout = 30.0


def is_responsive(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False

    
@pytest.fixture(scope="session")
def mdb_versioned(docker_services, docker_ip):
    bolt_port = docker_services.port_for("mdb-versioned", 7687)
    http_port = docker_services.port_for("mdb-versioned", 7474)
    bolt_url = "bolt://{}:{}".format(docker_ip, bolt_port)
    http_url = "http://{}:{}".format(docker_ip, http_port)
    sleep(wait)
    docker_services.wait_until_responsive(
        timeout=timeout, pause=1.0, check=lambda: is_responsive(http_url)
    )
    return (bolt_url, http_url)

@pytest.fixture(scope="session")
def mdb_dev(docker_services, docker_ip):
    bolt_port = docker_services.port_for("mdb-dev", 7687)
    http_port = docker_services.port_for("mdb-dev", 7474)
    bolt_url = "bolt://{}:{}".format(docker_ip, bolt_port)
    http_url = "http://{}:{}".format(docker_ip, http_port)
    sleep(wait)
    docker_services.wait_until_responsive(
        timeout=timeout, pause=1.0, check=lambda: is_responsive(http_url)
    )
    return (bolt_url, http_url)


@pytest.fixture
def app_on_test(mdb_versioned):
    (bolt, h) = mdb_versioned

    class TestConfig(Config):
        NEO4J_MDB_URI = bolt

    app = create_app(TestConfig)
    app.testing = True
    return app


@pytest.fixture
def app_on_dev(mdb_dev):
    (bolt, h) = mdb_dev

    class TestConfig(Config):
        NEO4J_MDB_URI = bolt

    app = create_app(TestConfig)
    app.testing = True
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
