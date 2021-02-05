from dataclasses import dataclass, field

@dataclass
class Node:
    handle: str = field()
    nanoid: str = field()
    model: str = field()
    kind: str = 'node'
    props: list = field(default_factory=list, compare=False, repr=False)
