import pytest
from bento_sts.config import Config
from bento_meta.util.makeq import Query

def test_query():
    Query.set_paths(Config.QUERY_PATHS)
    pth = "/model/ICDC/node/demographic/property/breed/term/Beagle"
    pth2 = "/model/ICDC/node/demographic/property/breed/term/German Shepherd Dog"
    assert Query.paths
    qq = Query(pth, use_cache=False)
    assert "Beagle" in qq.params.values()
    qq = Query(pth2, use_cache=False)
    assert "German Shepherd Dog" in qq.params.values()
    # do it again
    qq = Query(pth, use_cache=False)
    assert "Beagle" in qq.params.values()

if __name__ == '__main__':
    test_query()

    
