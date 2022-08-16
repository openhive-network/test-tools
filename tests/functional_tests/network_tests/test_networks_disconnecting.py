from enum import Enum
from typing import Iterable

import pytest

from local_tools.network import enable_debug_mode, get_head_block_number, get_head_block_numbers_for_networks
import test_tools as tt


class DisconnectionType(Enum):
    DISCONNECT_FROM = 1
    DISCONNECT_FROM_REVERSE = 2
    DISCONNECT_ALL = 3


def disconnect_two_networks_in_specified_way(
    first_network: tt.Network, second_network: tt.Network, disconnection_type: DisconnectionType
) -> None:
    if disconnection_type == DisconnectionType.DISCONNECT_FROM:
        tt.logger.info("Disconnecting first_network from second_network")
        first_network.disconnect_from(second_network)
    elif disconnection_type == DisconnectionType.DISCONNECT_FROM_REVERSE:
        tt.logger.info("Disconnecting second_network from first_network")
        second_network.disconnect_from(first_network)
    elif disconnection_type == DisconnectionType.DISCONNECT_ALL:
        tt.logger.info("Disconnecting first_network from all")
        first_network.disconnect_from_all()
    else:
        raise ValueError(f"Unknown disconnection type: {disconnection_type}")


@pytest.mark.parametrize(argnames="disconnection_type", argvalues=list(DisconnectionType))
def test_disconnecting_2_networks(disconnection_type: DisconnectionType, two_networks_connected: Iterable[tt.Network]):
    # ARRANGE
    first_network, second_network = two_networks_connected
    enable_debug_mode(networks=two_networks_connected)

    for network in two_networks_connected:
        network.run()

    # ACT
    disconnect_two_networks_in_specified_way(first_network, second_network, disconnection_type)
    first_network.node("InitNode0").wait_number_of_blocks(1)

    # ASSERT
    head_block_numbers = get_head_block_numbers_for_networks(networks=two_networks_connected)

    assert head_block_numbers[first_network] != head_block_numbers[second_network]


@pytest.mark.parametrize(
    argnames="disconnection_type",
    argvalues=[DisconnectionType.DISCONNECT_FROM, DisconnectionType.DISCONNECT_FROM_REVERSE],
)
def test_disconnecting_1_of_3_networks(
    disconnection_type: DisconnectionType, three_networks_connected: Iterable[tt.Network]
):
    # ARRANGE
    first_network, second_network, _ = three_networks_connected
    enable_debug_mode(networks=three_networks_connected)

    for network in three_networks_connected:
        network.run()

    # ACT
    second_network_head_num_before_disconnect = get_head_block_number(second_network)

    disconnect_two_networks_in_specified_way(first_network, second_network, disconnection_type)
    first_network.node("InitNode0").wait_number_of_blocks(1)

    second_network.node("ApiNode0").wait_for_block_with_number(
        second_network_head_num_before_disconnect + 1, timeout=60
    )

    # ASSERT
    head_block_numbers = get_head_block_numbers_for_networks(three_networks_connected)

    assert head_block_numbers[second_network] > second_network_head_num_before_disconnect


@pytest.mark.parametrize("disconnection_type", [DisconnectionType.DISCONNECT_FROM, DisconnectionType.DISCONNECT_ALL])
def test_separating_1_from_3_networks(
    disconnection_type: DisconnectionType, three_networks_connected: Iterable[tt.Network]
):
    # ARRANGE
    first_network, second_network, third_network = three_networks_connected
    enable_debug_mode(networks=three_networks_connected)

    for network in three_networks_connected:
        network.run()

    # ACT
    if disconnection_type == DisconnectionType.DISCONNECT_FROM:
        tt.logger.info("Disconnecting first_network from second_network and third_network")
        first_network.disconnect_from(second_network)
        first_network.disconnect_from(third_network)
    elif disconnection_type == DisconnectionType.DISCONNECT_ALL:
        tt.logger.info("Disconnecting first_network from all networks")
        first_network.disconnect_from_all()

    first_network.node("InitNode0").wait_number_of_blocks(1)

    # ASSERT
    head_block_numbers = get_head_block_numbers_for_networks(three_networks_connected)

    assert head_block_numbers[first_network] != head_block_numbers[second_network]
    assert head_block_numbers[second_network] == head_block_numbers[third_network]
