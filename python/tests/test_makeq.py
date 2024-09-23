import pytest
from bento_sts.config import Config
from bento_sts.query import Query


def test_query():
    Query.set_paths(Config.QUERY_PATHS)
    pth = "/model/ICDC/version/1.0/node/demographic/property/breed/term/Beagle"
    pth2 = "/model/ICDC/version/1.0/node/demographic/property/breed/term/German Shepherd Dog"
    assert Query.paths
    qq = Query(pth)
    assert "Beagle" in qq.params.values()
    qq = Query(pth2)
    assert "German Shepherd Dog" in qq.params.values()
    # do it again
    qq = Query(pth)
    assert "Beagle" in qq.params.values()


def test_paths(test_paths):
    assert Query.set_paths(Config.QUERY_PATHS)
    assert len(test_paths)

    q = Query("/model/ICDC/version/1.0/node/demographic/property/breed/terms")
    q = Query("/tag/Category/values")
    assert q.path_id == "tag_values"
    q = Query("/tag/Category/administrative/entities")
    assert q.path_id == "tag_entities"
    
    for t in test_paths:
        qq = Query(t)
        assert qq.statement
        assert isinstance(qq.params, dict)
        pass
    
    # this is a test of the "engine caching" - OBE
    # q1 = Query("/tag/this/that/entities/count")
    # list(q.params.values()) == ["this","that"]
    # q2 = Query("/tag/13/other/entities/count")
    # list(q.params.values()) == [13, "other"]
    # assert q1._engine == q2._engine
    

if __name__ == '__main__':
    test_query()

    
