# This test forces that create_default_config will be always up to date.
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import test_tools as tt
from test_tools.node_configs.default import create_default_config

if TYPE_CHECKING:
    from test_tools.__private.node_config import NodeConfig


@pytest.fixture()
def generated_config() -> NodeConfig:
    node = tt.RawNode()
    node.set_cleanup_policy(tt.constants.CleanupPolicy.REMOVE_EVERYTHING)
    node.dump_config()

    return node.config


def test_default_config_values(generated_config: NodeConfig) -> None:
    default_config = create_default_config(skip_address=True)
    if default_config != generated_config:
        print("Found differences:")  # noqa: T201
        differences = default_config.get_differences_between(generated_config)

        for key, (default_value, generated_value) in differences.items():
            print(  # noqa: T201
                f"""{key}

In default_config: {default_value} {type(default_value)}
Generated:         {generated_value} {type(generated_value)}"""
            )

        raise AssertionError("Modify config returned from create_default_config to match default generated config")
