from test_tools.private.children_names import ChildrenNames
from test_tools.private.node import Node


class NodesCreator:
    def __init__(self):
        self._children_names = ChildrenNames()
        self._nodes = []

    def node(self, name: str) -> Node:
        for node in self._nodes:
            if node.get_name() == name:
                return node

        raise RuntimeError(
            f'There is no node with name "{name}". Available nodes are:\n'
            f'{[node.get_name() for node in self._nodes]}'
        )

    def nodes(self):
        return self._nodes

    def _handle_final_cleanup(self):
        for node in self._nodes:
            node.handle_final_cleanup()
