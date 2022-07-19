from __future__ import annotations

import typing
from typing import Dict
from typing import List
from typing import Optional

from test_tools.__private.network import Network
from test_tools.__private.user_handles.get_implementation import get_handle
from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.user_handles.handle import Handle
from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as Node


class NetworkHandle(Handle):
    def __init__(self):
        super().__init__(
            implementation=Network(handle=self)
        )

    @property
    def __implementation(self) -> Network:
        return typing.cast(Network, get_implementation(self))

    def connect_with(self, network: NetworkHandle) -> None:
        """
        Connects nodes in this network with nodes from other network, passed as `network` parameter. Networks can be
        connected only in two situations:
        - before any node start,
        - after previous disconnection with `disconnect_from` method.

        :param network: Network to connect with.
        """
        return self.__implementation.connect_with(
            get_implementation(network)
        )

    def disconnect_from(self, network: NetworkHandle) -> None:
        """
        Disables communication between nodes in this network and nodes from other network, passed as `network`
        parameter. Only networks connected with `connect_with` method can be disconnected.

        :param network: Network to disconnect from.
        """
        return self.__implementation.disconnect_from(
            get_implementation(network)
        )

    def node(self, name: str) -> Node:
        """
        Returns node with specified `name`.

        :param name: Name of node to retrieve.
        """
        node = self.__implementation.node(name)
        return typing.cast(Node, get_handle(node))

    @property
    def nodes(self) -> List[Node]:
        """Returns all nodes within network."""
        return [typing.cast(Node, get_handle(node)) for node in self.__implementation.nodes]

    def run(self, environment_variables: Optional[Dict[str, str]] = None) -> None:
        """
        Runs all nodes within network with default startup parameters. Blocks execution until all nodes enter live mode.

        :param environment_variables: Additional environment variables passed to each node before start.
        """
        return self.__implementation.run(environment_variables=environment_variables)
