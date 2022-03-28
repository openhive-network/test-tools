from __future__ import annotations

import typing
from typing import List

from test_tools.network import Network
from test_tools.private.user_handles.get_implementation import get_implementation, get_handle
from test_tools.private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as Node


class NetworkHandle:
    def __init__(self):
        self.__implementation = Network()

    def connect_with(self, network: NetworkHandle) -> None:
        return self.__implementation.connect_with(
            get_implementation(network)
        )

    def disconnect_from(self, network: NetworkHandle) -> None:
        return self.__implementation.disconnect_from(
            get_implementation(network)
        )

    def node(self, name: str) -> Node:
        node = self.__implementation.node(name)
        return typing.cast(Node, get_handle(node))

    @property
    def nodes(self) -> List[Node]:
        return [typing.cast(Node, get_handle(node)) for node in self.__implementation.nodes]

    def run(self) -> None:
        return self.__implementation.run()
