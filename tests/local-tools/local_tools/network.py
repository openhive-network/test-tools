from typing import Dict, Optional

from typing import Iterable

import pytest
import test_tools as tt


def enable_debug_mode(
    *, nodes: Optional[Iterable[tt.RawNode]] = None, networks: Optional[Iterable[tt.Network]] = None
) -> None:
    nodes = [] if nodes is None else nodes
    networks = [] if networks is None else networks

    for network in networks:
        nodes.extend(network.nodes)

    for node in nodes:
        node.config.webserver_thread_pool_size = "2"
        node.config.blockchain_thread_pool_size = 2
        node.config.log_logger = (
            '{"name":"default","level":"debug","appender":"stderr,p2p"} '
            '{"name":"user","level":"debug","appender":"stderr,p2p"} '
            '{"name":"chainlock","level":"debug","appender":"p2p"} '
            '{"name":"sync","level":"debug","appender":"p2p"} '
            '{"name":"p2p","level":"debug","appender":"p2p"}'
        )


def get_head_block_number(network: tt.Network) -> int:
    node = network.nodes[0]
    return node.api.database.get_dynamic_global_properties()["head_block_number"]


def get_head_block_numbers_for_networks(networks: Iterable[tt.Network]) -> Dict[tt.Network, int]:
    head_block_numbers = {}
    for network in networks:
        head_block_number = get_head_block_number(network)
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
