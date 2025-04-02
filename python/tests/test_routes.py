import pytest
import yaml
from flask import Flask
from flask_bootstrap import Bootstrap4
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect
from bento_sts.api.routes import bp as api_bp
from bento_sts.main.routes import bp as main_bp
from unittest.mock import Mock
from pdb import set_trace



class MockMDB(Mock):
    @staticmethod
    def get_model_pvs_synonyms(model, version):
        return {}
    @staticmethod
    def get_cde_pvs_by_id(cde_id, cde_version):
        return {}
    @staticmethod
    def get_term_nanoid_by_origin(origin_name, origin_id, origin_version):
        return {}


mdb = MockMDB()

def set_mdb_responses(resps=[]):
    it = iter(resps)
    mdb.get_with_statement = lambda x, y=None: next(it)
        

bootstrap4 = Bootstrap4()
moment = Moment()
csrf = CSRFProtect()

@pytest.fixture
def app():
    app = Flask(__name__,
                template_folder="../src/bento_sts/templates")
    app.config['TESTING'] = True
    app.config['MAX_ENTS_PER_REQ'] = 100
    app.config['NEO4J_MDB_URI'] = 'bolt://localhost:7687'
    app.config['NEO4J_MDB_USER'] = 'neo4j'
    app.config['NEO4J_MDB_PASS'] = 'neo4j1'
    app.config['QUERY_PATHS'] = yaml.load(open("tests/query_paths.yml","r"), Loader=yaml.CLoader)
    app.config['WTF_CSRF_SECRET_KEY'] = 'superdupersekr1t'
    app.config['MDB'] = mdb
    app.register_blueprint(api_bp)
    app.register_blueprint(main_bp)
    app.secret_key = 'superdupersekr1t'
    bootstrap4.init_app(app)
    moment.init_app(app)
    csrf.init_app(app)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['application'] == 'STS'
    assert data['version'] == '0.1'
    assert data['status'] == 'READY'

def test_query_db(client):
    set_mdb_responses([
        [{'count': 1}],
        [{'key': 'value'}]
    ])
    response = client.get('/v1/models')
    assert response.status_code == 200
    data = response.get_json()
    assert data == {'count': 1, 'key': 'value'}

def test_query_db_no_results(client):
    set_mdb_responses([
        [{'count': 0}],
        []
    ])
    response = client.get('/v1/models')
    assert response.status_code == 404

def test_query_db_mdb_issue(client):
    mdb.get_with_statement = Mock(side_effect=Exception('Whoa dude'))
    response = client.get('/v1/models')
    assert response.status_code == 500
    data = response.get_json()
    assert 'MDB issue' in data['description']

def test_api_pv_paths(client):
    set_mdb_responses([
        [{'count': 1}],
        [{'key': 'value'}]
    ])
    response = client.get('/v1/terms/model-pvs/ICDC/1.0/pvs')
    assert response.status_code == 200
    set_mdb_responses([
        [{'count': 1}],
        [{'key': 'value'}]
    ])
    response = client.get('/v1/terms/cde-pvs/14425/1.0/pvs')
    assert response.status_code == 200
    # negative control:
    response = client.get('/v1/terms/cde-pvs/14425/1.0')    
    assert response.status_code == 404

def test_main_pv_paths(client):
    set_mdb_responses([
        [{'count': 1}],
        [{'key': 'value'}]
    ])
    response = client.get('/model-pvs/ICDC/1.0')
    assert response.status_code == 200
    set_mdb_responses([
        [{'count': 1}],
        [{'key': 'value'}]
    ])
    response = client.get('/v1/terms/cde-pvs/14425/1.0/pvs')
    assert response.status_code == 200
    # negative control:
    response = client.get('/v1/terms/cde-pvs/14425/1.0')    
    assert response.status_code == 404
    
