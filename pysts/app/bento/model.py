from dataclasses import dataclass, field
# from app.bento.node import Node

@dataclass
class Model:
    handle: str = field()
    nanoid: str = field()
    kind: str = 'model'
    nodes: list = field(default_factory=list, compare=False, repr=False)