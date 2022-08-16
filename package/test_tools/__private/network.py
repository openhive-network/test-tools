from __future__ import annotations

from typing import Dict, Optional, TYPE_CHECKING

from test_tools.__private.logger.logger_internal_interface import logger
from test_tools.__private.scope import context
from test_tools.__private.user_handles.implementation import Implementation as UserHandleImplementation

if TYPE_CHECKING:
    from test_tools.__private.node import Node
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle


class Network(UserHandleImplementation):
    def __init__(self, name: str = 'Network', handle: Optional[NetworkHandle] = None):
        super().__init__(handle=handle)

        self.name = context.names.register_numbered_name(name)
        self.nodes = []
        self.network_to_connect_with = None
        self.disconnected_networks = []
        self.logger = logger.create_child_logger(str(self))

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return str(self)

    def add(self, node: Node) -> None:
        self.nodes.append(node)

    def node(self, name: str) -> Node:
        for node in self.nodes:
            if node.get_name() == name:
                return node

        raise RuntimeError(f'There is no node with name {name} in network {self}')

    def run(self, wait_for_live: Optional[bool] = None, environment_variables: Optional[Dict[str, str]] = None):
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
            node.config.p2p_seed_node.append(endpoint)
            node.run(wait_for_live=wait_for_live, environment_variables=environment_variables)

    def connect_with(self, network):
        if len(self.nodes) == 0 or len(network.nodes) == 0:
            raise Exception('Unable to connect empty network')

        if not any(node.is_running() for node in self.nodes):
            if any(node.is_able_to_produce_blocks() for node in self.nodes):
                network.network_to_connect_with = self
            else:
                self.network_to_connect_with = network
            return

        if network not in self.disconnected_networks:
            raise Exception('Unsupported: cannot connect networks when were already run and not disconnected before')

        # Temporary implementation working only with one network
        self.allow_for_connections_with_anyone()
        self.disconnected_networks.remove(network)

        network.allow_for_connections_with_anyone()
        network.disconnected_networks.remove(self)

    def disconnect_from(self, network):
        if len(self.nodes) == 0 or len(network.nodes) == 0:
            raise Exception('Unable to disconnect empty network')

        self.disconnected_networks.append(network)
        network.disconnected_networks.append(self)

        self.allow_for_connections_only_between_nodes_in_network()
        network.allow_for_connections_only_between_nodes_in_network()

    def allow_for_connections_only_between_nodes_in_network(self):
        for node_number, node in enumerate(self.nodes):
            node.set_allowed_nodes(self.nodes[:node_number] + self.nodes[node_number+1:])

    def allow_for_connections_with_anyone(self):
        for node in self.nodes:
            node.set_allowed_nodes([])
