from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from test_tools.__private.process.node_config import NodeConfig


def test_adding_item_to_empty_list(config: NodeConfig) -> None:
    config.witness.append("A")
    assert config.witness == ["A"]


def test_adding_multiple_items_in_single_line(config: NodeConfig) -> None:
    config.private_key.extend(["1", "2", "3"])
    assert config.private_key == ["1", "2", "3"]


def test_adding_multiple_items_in_few_lines(config: NodeConfig) -> None:
    config.private_key.append("1")
    config.private_key.append("2")
    config.private_key.append("3")
    assert config.private_key == ["1", "2", "3"]


def test_adding_first_string_instead_of_list(config: NodeConfig) -> None:
    config.private_key.append("5KFirstQmyBxGKqXCv5qRhip")
    assert config.private_key == ["5KFirstQmyBxGKqXCv5qRhip"]


def test_adding_second_string_instead_of_list(config: NodeConfig) -> None:
    config.private_key = ["5KFirstQmyBxGKqXCv5qRhip"]
    config.private_key.append("5KSecondXPdzYqB8d6S66bup")
    assert config.private_key == ["5KFirstQmyBxGKqXCv5qRhip", "5KSecondXPdzYqB8d6S66bup"]


def test_remove_item_from_list(config: NodeConfig) -> None:
    config.plugin.clear()
    config.plugin.extend(["witness", "account_by_key", "account_by_key_api", "condenser_api"])
    config.plugin.remove("witness")
    assert sorted(config.plugin) == sorted(["account_by_key", "account_by_key_api", "condenser_api"])
