"""
makeq - make a Neo4j query from an endpoint path or JSON payload.
"""
import yaml

from pdb import set_trace
from ._engine import _engine

class Query(object):
    paths = {}
    cache = {}

    def __init__(self, qspec):
        if isinstance(qspec, str):
            path = qspec
            if path.startswith("/"):
                path = path[1:]
            self.toks = path.split("/")
            self._engine = None
            if not self._engine:
                self._engine = _engine()
                if not self._engine.parse(self.toks):
                    raise RuntimeError(self._engine.error)
        elif isinstance(qspec, dict):
            pass
        else:
            raise RuntimeError("Query arg1 must be path string or dict")

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
