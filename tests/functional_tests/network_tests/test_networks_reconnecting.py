from typing import Iterable

from local_tools.network import enable_debug_mode, get_head_block_number, get_head_block_numbers_for_networks
import test_tools as tt


def test_reconnecting_2_networks(two_networks_connected: Iterable[tt.Network]):
    # ARRANGE
    first_network, second_network = two_networks_connected
    enable_debug_mode(networks=two_networks_connected)

    for network in two_networks_connected:
        network.run()

    # ACT
    second_network_head_num_before_disconnect = get_head_block_number(second_network)

    tt.logger.info("Disconnecting first_network from second_network")
    first_network.disconnect_from(second_network)
    first_network.node("InitNode0").wait_number_of_blocks(1)

    tt.logger.info("Connecting first_network with second_network")
    first_network.connect_with(second_network)
    second_network.node("ApiNode0").wait_for_block_with_number(
        second_network_head_num_before_disconnect + 1, timeout=60
    )

    # ASSERT
    head_block_numbers = get_head_block_numbers_for_networks(two_networks_connected)

    assert head_block_numbers[second_network] > second_network_head_num_before_disconnect


def test_reconnecting_3_networks(three_networks_connected: Iterable[tt.Network]):
    # ARRANGE
    first_network, second_network, third_network = three_networks_connected
    enable_debug_mode(networks=three_networks_connected)

    for network in three_networks_connected:
        network.run()

    # ACT
    second_network_head_num_before_disconnect = get_head_block_number(second_network)
    third_network_head_num_before_disconnect = get_head_block_number(third_network)

    tt.logger.info("Disconnecting first_network from all networks")
    first_network.disconnect_from_all()
    first_network.node("InitNode0").wait_number_of_blocks(1)

    tt.logger.info("Connecting first_network with second_network")
    first_network.connect_with(second_network)
    tt.logger.info("Connecting first_network with third_network")
    first_network.connect_with(third_network)
    second_network.node("ApiNode0").wait_for_block_with_number(
        second_network_head_num_before_disconnect + 1, timeout=60
    )
    third_network.node("ApiNode1").wait_for_block_with_number(third_network_head_num_before_disconnect + 1, timeout=60)

    # ASSERT
    head_block_numbers = get_head_block_numbers_for_networks(three_networks_connected)

    assert head_block_numbers[second_network] > second_network_head_num_before_disconnect
    assert head_block_numbers[third_network] > third_network_head_num_before_disconnect
