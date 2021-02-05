from app.bento.node import Node

def get_node_a():
    n = Node(handle='cycle',
             nanoid='123abc',
             model='test',
             kind='node')
    return n

def test_doe():
    node_a = get_node_a()
    print(node_a)
    assert node_a.kind == 'node'
