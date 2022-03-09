from test_tools.private.node import Node


class RawNode(Node):
    def __init__(self, *, name: str = 'RawNode'):
        super().__init__(name=name)
