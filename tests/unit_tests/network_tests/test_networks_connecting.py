from typing import Iterable

import pytest

import test_tools as tt

# pylint: disable=protected-access


def test_connecting_two_networks(two_networks_connected: Iterable[tt.Network]):
    # ARRANGE AND ACT is done in two_networks_connected fixture
    first_network, second_network = two_networks_connected

    # ASSERT
    assert (
        second_network._NetworkHandle__implementation in first_network._NetworkHandle__implementation.connected_networks
    )
    assert (
        first_network._NetworkHandle__implementation in second_network._NetworkHandle__implementation.connected_networks
    )


@pytest.mark.parametrize(
    "broadcast", argvalues=[True, False], ids=("first_connecting_to_third_only", "second_connecting_to_third_also")
)
def test_connecting_three_networks(broadcast: bool, three_networks_connected: Iterable[tt.Network]):
    # ARRANGE AND ACT is partly done in two_networks_connected fixture
    first_network, second_network, third_network = three_networks_connected

    # ACT
    # we don't have to connect second_network with third_network, because first_network will broadcast the connections
    if not broadcast:
        second_network.connect_with(third_network)

    # ASSERT
    assert first_network._NetworkHandle__implementation.connected_networks == {
        second_network._NetworkHandle__implementation,
        third_network._NetworkHandle__implementation,
    }

    assert second_network._NetworkHandle__implementation.connected_networks == {
        first_network._NetworkHandle__implementation,
        third_network._NetworkHandle__implementation,
    }

    assert third_network._NetworkHandle__implementation.connected_networks == {
        first_network._NetworkHandle__implementation,
        second_network._NetworkHandle__implementation,
    }


def test_connecting_four_networks(four_networks_connected: Iterable[tt.Network]):
    # ARRANGE AND ACT is partly done in four_networks_connected fixture
    first_network, second_network, third_network, fourth_network = four_networks_connected

    # ASSERT
    assert first_network._NetworkHandle__implementation.connected_networks == {
        second_network._NetworkHandle__implementation,
        third_network._NetworkHandle__implementation,
        fourth_network._NetworkHandle__implementation,
    }
    assert second_network._NetworkHandle__implementation.connected_networks == {
        first_network._NetworkHandle__implementation,
        third_network._NetworkHandle__implementation,
        fourth_network._NetworkHandle__implementation,
    }
    assert third_network._NetworkHandle__implementation.connected_networks == {
        first_network._NetworkHandle__implementation,
        second_network._NetworkHandle__implementation,
        fourth_network._NetworkHandle__implementation,
    }
    assert fourth_network._NetworkHandle__implementation.connected_networks == {
        first_network._NetworkHandle__implementation,
        second_network._NetworkHandle__implementation,
        third_network._NetworkHandle__implementation,
    }
