import os
import pprint
import json
from flask import url_for, current_app
from app import logging
from neo4j import GraphDatabase
from bento_meta.model import Model
from bento_meta.mdf import MDF
from bento_meta.diff import diff_models
from bento_meta.object_map import ObjectMap


'''Phase 1: test diff works'''
def get_diff():
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
    APP_STATIC = os.path.join(APP_ROOT, 'static')
    yml_a = os.path.join(APP_STATIC, "test-model-c.yml")
    yml_b = os.path.join(APP_STATIC, "test-model-d.yml")
    a = MDF(yml_a, handle='test1')
    b = MDF(yml_b, handle='test1')

    #logger = logging.getLogger()
    #logger.info('test message')

    delta = diff_models(a.model, b.model)
    current_app.logger.error('test test test')
    pprint.pprint(delta)
    return delta


'''Phase 1: test diff works'''
def diff_mdf(mdf_file_a, mdf_file_b):
    # APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
    # APP_STATIC = os.path.join(APP_ROOT, 'static')
    APP_UPLOAD_PATH = current_app.config['UPLOAD_PATH']
    mdf_a = os.path.join(APP_UPLOAD_PATH, mdf_file_a)
    mdf_b = os.path.join(APP_UPLOAD_PATH, mdf_file_b)

    a = MDF(mdf_a, handle='test1')
    b = MDF(mdf_b, handle='test1')

    #logger = logging.getLogger()
    #logger.info('test message')

    delta = diff_models(a.model, b.model)
    current_app.logger.error('FINISHING diff_mdf')
    pprint.pprint(delta)
    return delta


class jet():
    '''TO BE DEPRECATED'''

    def __init__(self):
        self.uri = os.environ.get("NEO4J_MDB_URI")
        self.user = os.environ.get("NEO4J_MDB_USER")
        self.password = os.environ.get("NEO4J_MDB_PASS")

        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    def diff(self, yml):
        # take yml
        mdf = MDF(yml, handle='test ')
        pass

    def get_model_by_name(self, name):
        ObjectMap.clear_cache()
        model = Model(name, self.driver)
        # if you dont call dget, it wont be populated...
        model.dget()
        return model
