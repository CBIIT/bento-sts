"""
makeq - make a Neo4j query from an endpoint path.
"""
import yaml
import re
from pdb import set_trace
from ._engine import _engine
from bento_meta.util.cypher.entities import (  # noqa E402
    N, R, P, N0, R0, G,
    _as, _var, _plain, _anon,
    )
from bento_meta.util.cypher.functions import (
    count, exists, labels, group, And, Or, Not,
    )
from bento_meta.util.cypher.clauses import (
    Match, Where, With, Return,
    Statement,
    )

class Query(object):
    paths = {}
    cache = {}

    def __init__(self, path):
        if path.startswith("/"):
            path = path[1:]
        self.toks = path.split("/")
        self._engine = None
        if not self._engine:
            self._engine = _engine()
            if not self._engine.parse(self.toks):
                raise RuntimeError(self._engine.error)

    @classmethod
    def set_paths(cls, paths):
        if paths.get('paths'):
            cls.paths = paths['paths']
        else:
            cls.paths = paths
        _engine.set_paths(cls.paths)
        return True

    @classmethod
    def load_paths(cls, flo):
        p = yaml.load(flo, Loader=yaml.CLoader)
        return cls.set_paths(p)


    @property
    def statement(self):
        return self._engine.statement

    @property
    def params(self):
        return self._engine.params

    @property
    def path_id(self):
        return self._engine.path_id
    
    def __str__(self):
        return str(self.statement)


def f(pfx, pth):
    tok = [x for x in pth if x.startswith('$')]
    if not tok:
        tok = [x for x in pth if not x.startswith('_')]
    if not tok:
        print(pfx)
        return
    else:
        if pth.get('_return'):
            print(pfx)
        for t in tok:
            f('/'.join([pfx, t]), pth[t])
        return
