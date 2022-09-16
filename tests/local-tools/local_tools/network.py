from __future__ import annotations

from typing import Dict, Iterable, Optional

import pytest

import test_tools as tt


def get_head_block_number(*, node: Optional[tt.AnyNode] = None, network: Optional[tt.Network] = None) -> int:
    if not node and not network:
        raise ValueError("Either node or network must be provided")

    _node = node or network.nodes[0]
    return _node.api.database.get_dynamic_global_properties()["head_block_number"]


def get_head_block_numbers_for_networks(networks: Iterable[tt.Network]) -> Dict[tt.Network, int]:
    head_block_numbers = {}
    for network in networks:
        head_block_number = get_head_block_number(network=network)
        tt.logger.info(f"Head block number of {network} is {head_block_number}")
        head_block_numbers[network] = head_block_number
    return head_block_numbers


@pytest.fixture
def two_networks_connected() -> Iterable[tt.Network]:
    # ARRANGE
    first_network = tt.Network()
    tt.InitNode(network=first_network)

    second_network = tt.Network()
    tt.ApiNode(network=second_network)

    # ACT
    first_network.connect_with(second_network)

    networks = [first_network, second_network]

    return networks


@pytest.fixture
def three_networks_connected(two_networks_connected: Iterable[tt.Network]) -> Iterable[tt.Network]:
    # ARRANGE AND ACT is partly done in two_networks_connected fixture
    first_network, second_network = two_networks_connected

    # ARRANGE
    third_network = tt.Network()
    tt.ApiNode(network=third_network)

    # ACT
    # we don't have to connect second_network with third_network, because first_network will broadcast the connections
    first_network.connect_with(third_network)

    networks = [first_network, second_network, third_network]
    return networks


@pytest.fixture
def four_networks_connected(three_networks_connected: Iterable[tt.Network]) -> Iterable[tt.Network]:
    # ARRANGE AND ACT is partly done in three_networks_connected fixture
    first_network, second_network, third_network = three_networks_connected

    # ARRANGE
    fourth_network = tt.Network()
    tt.ApiNode(network=fourth_network)

    # ACT
    first_network.connect_with(fourth_network)

    networks = [first_network, second_network, third_network, fourth_network]
    return networks
