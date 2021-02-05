import pytest
from app.bento.n4jdb import N4jdb


def get_message(n4jdb, message):
    """uses n4jdb"""
    with n4jdb.driver.session() as session:
        result = session.run("CREATE (a:Greeting) "
                             "SET a.message = $message "
                             "RETURN a.message + ', from neo4j'", message=message)
        return result.single()[0]


def get_neo4j_server_info(n4jdb):
    """uses n4jdb"""
    with n4jdb.driver.session() as session:
        result = session.run("call dbms.components() yield versions, edition "
                             "unwind versions as version "
                             "return version, edition;")
        return result.single()


@pytest.mark.skip(reason="for neo4j in docker")
def test_docker_neo4j_access(docker_bento_neo4j):
    with N4jdb(docker_bento_neo4j) as n4jdb:
        test_message = 'hello, world'
        actual_message = get_message(n4jdb, test_message)
        expected_message = 'hello, world, from neo4j'
        assert actual_message == expected_message


@pytest.mark.skip(reason="for neo4j in docker")
def test_docker_neo4j_version(docker_bento_neo4j):
    with N4jdb(docker_bento_neo4j) as n4jdb:
        (version, edition) = get_neo4j_server_info(n4jdb)
        assert version == '3.5.3'
        assert edition == 'community'


def test_local_neo4j_access_a():
    """test use Neo4j Desktop"""
    with N4jdb() as n4jdb:
        test_message = 'hello, world'
        actual_message = get_message(n4jdb, test_message)
        expected_message = 'hello, world, from neo4j'
        assert actual_message == expected_message


def test_local_neo4j_version():
    """test use Neo4j Desktop"""
    with N4jdb() as n4jdb:
        (version, edition) = get_neo4j_server_info(n4jdb)
        assert version == '3.5.17'
        assert edition == 'enterprise'