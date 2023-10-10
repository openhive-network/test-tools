# These tests checks if access to nonexistent keys in config are reported as errors.
#
# For example user should write:
# but, might by accident write (note double 'n' in 'witness'):
#
# Then exception will be raised and error will be immediately noticed.
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from test_tools.__private.node_config import NodeConfig


def test_getting_unset_but_correct_entry(config: NodeConfig) -> None:
    assert config.required_participation is None


def test_setting_correct_entry(config: NodeConfig) -> None:
    config.required_participation = 33
