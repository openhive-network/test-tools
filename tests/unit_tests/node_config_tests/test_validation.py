from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from test_tools.__private.process.node_config import NodeConfig


def test_detection_of_duplicated_plugins(config: NodeConfig) -> None:
    config.plugin.extend(["condenser_api", "condenser_api"])
    assert config.write_to_lines() == ["plugin = condenser_api"]
