from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from test_tools.__private.exceptions import TestToolsError
from test_tools.__private.scope import context
from test_tools.__private.user_handles.implementation import Implementation as UserHandleImplementation

if TYPE_CHECKING:
    from loguru import Logger

    from test_tools.__private.node import Node
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle


class ConnectToEmptyNetworkError(TestToolsError):
    def __init__(self, *args: object) -> None:
        super().__init__("Unable to connect empty network", *args)


class UnsupportedNetworkConnectionError(TestToolsError):
    def __init__(self, *args: object) -> None:
        super().__init__(
            "Unsupported: cannot connect networks when were already run and not disconnected before", *args
        )


class UnableToDisconnectEmptyNetworkError(TestToolsError):
    def __init__(self, *args: object) -> None:
        super().__init__("Unable to disconnect empty network", *args)


class Network(UserHandleImplementation):
    def __init__(self, name: str = "Network", handle: NetworkHandle | None = None) -> None:
        super().__init__(handle=handle)

        self.name = context.names.register_numbered_name(name)
        self.nodes: list[Node] = []
        self.network_to_connect_with: Network | None = None
        self.connected_networks: set[Network] = set()
        self.disconnected_networks: set[Network] = set()

    @property
    def logger(self) -> Logger:
        return logger

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    def add(self, node: Node) -> None:
        self.nodes.append(node)

    def node(self, name: str) -> Node:
        for node in self.nodes:
            if node.get_name() == name:
                return node

        raise RuntimeError(f"There is no node with name {name} in network {self}")

    def run(self, wait_for_live: bool | None = None, environment_variables: dict[str, str] | None = None) -> None:
        if self.network_to_connect_with is None:
            seed_node = self.nodes[0]
            seed_node.run(wait_for_live=wait_for_live, environment_variables=environment_variables)
            nodes_connecting_to_seed = self.nodes[1:]
        else:
            seed_node = self.network_to_connect_with.nodes[0]
            self.network_to_connect_with = None
            nodes_connecting_to_seed = self.nodes

        endpoint = seed_node.get_p2p_endpoint()

        for node in nodes_connecting_to_seed:
            node.config.p2p_seed_node.append(str(endpoint))
            node.run(wait_for_live=wait_for_live, environment_variables=environment_variables)

    def connect_with(self, network: Network) -> None:
        if not self.nodes or not network.nodes:
            raise ConnectToEmptyNetworkError

        if any(node.is_running() for node in self.nodes):
            self.__connect_with_earlier_disconnected_network(network)
            return

        self.__prepare_connections_before_run(network)

    def __connect_with_earlier_disconnected_network(self, network: Network) -> None:
        if network not in self.disconnected_networks:
            raise UnsupportedNetworkConnectionError

        self.connected_networks.add(network)
        self.__update_connected_networks_in_child_networks()

        self.disconnected_networks.remove(network)

        self.__allow_for_connections_only_between_nodes_in_connected_networks()

    def __prepare_connections_before_run(self, network: Network) -> None:
        if any(node.is_able_to_produce_blocks() for node in self.nodes):
            network.network_to_connect_with = self
        else:
            self.network_to_connect_with = network

        self.connected_networks.add(network)
        self.__update_connected_networks_in_child_networks()

    def __update_connected_networks_in_child_networks(self) -> None:
        for child_network in self.connected_networks:
            networks = list(self.connected_networks)
            networks.remove(child_network)
            networks.append(self)
            child_network.connected_networks.update(networks)

    def disconnect_from(self, network: Network) -> None:
        if not self.nodes or not network.nodes:
            raise UnableToDisconnectEmptyNetworkError

        self.connected_networks.remove(network)
        self.disconnected_networks.add(network)
        self.__allow_for_connections_only_between_nodes_in_connected_networks()

    def __allow_for_connections_only_between_nodes_in_connected_networks(self) -> None:
        allowed_nodes = set(self.nodes)
        for network in self.connected_networks:
            allowed_nodes.update(network.nodes)

        self.logger.info(f"Allowing connections only with: {allowed_nodes}")
        for node in self.nodes:
            node.set_allowed_nodes(list(allowed_nodes))

    def disconnect_from_all(self) -> None:
        if not self.nodes:
            raise UnableToDisconnectEmptyNetworkError

        self.disconnected_networks.update(self.connected_networks)
        self.connected_networks.clear()

        self.logger.info(f"Allowing connections only with nodes in my network: {self.nodes}")
        for node in self.nodes:
            node.set_allowed_nodes(self.nodes)

    def allow_for_connections_with_anyone(self) -> None:
        self.logger.info("Allowing connections with anyone")
        for node in self.nodes:
            node.set_allowed_nodes([])
