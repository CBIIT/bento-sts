import os
from neo4j import GraphDatabase


class N4jdb:
    def __init__(self, uri=None, user=None, password=None):
        if uri is None:
            # uri = 'bolt://localhost:7687'
            uri = os.environ.get("NEO4J_MDB_URI")
        self.uri = uri

        if user is None:
            # user = 'neo4j'
            user = os.environ.get("NEO4J_MDB_USER")
        self.user = user

        if password is None:
            password = os.environ.get("NEO4J_MDB_PASS")
        self.password = password

        self.driver = None

    def __enter__(self):
        # connect to database
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        return self

    def __exit__(self, *args):
        self.driver.close()
