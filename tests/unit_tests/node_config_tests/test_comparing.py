from __future__ import annotations

import pytest
from test_tools.__private.node_config import NodeConfig

ConfigsFixtureReturn = tuple[NodeConfig, NodeConfig, NodeConfig]


@pytest.fixture()
def configs() -> ConfigsFixtureReturn:
    return NodeConfig(), NodeConfig(), NodeConfig()


def test_different_shared_file_size_values(configs: ConfigsFixtureReturn) -> None:
    first, second, empty = configs

    first.shared_file_size = "5G"
    second.shared_file_size = "42G"

    assert first != second
    assert first != empty
    assert second != empty


def test_different_required_participation_values(configs: ConfigsFixtureReturn) -> None:
    first, second, empty = configs

    first.required_participation = 1
    second.required_participation = 2

    assert first != second
    assert first != empty
    assert second != empty


def test_different_enable_stale_production_values(configs: ConfigsFixtureReturn) -> None:
    first, second, empty = configs

    first.enable_stale_production = True
    second.enable_stale_production = False

    assert first != second
    assert first != empty
    assert second != empty
