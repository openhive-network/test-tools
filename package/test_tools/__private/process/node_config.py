from __future__ import annotations

from typing import Any

from beekeepy._executable.abc import Config

from test_tools.__private.process.node_common import NodeCommon


# All config items are automatically generated
class NodeConfig(NodeCommon, Config):
    """Parameters used in config file."""

    @classmethod
    def default(cls) -> NodeConfig:
        return cls()

    def write_to_lines(self) -> list[str]:
        self.deduplicate()
        return super().write_to_lines()

    @classmethod
    def from_lines(cls, lines: list[str]) -> NodeConfig:
        result = super().from_lines(lines)
        result.deduplicate()
        return result

    def deduplicate(self) -> None:
        """Remove duplicate entries from the config."""
        for member_name, member_value in self.dict(exclude_defaults=True, exclude_none=True).items():
            if isinstance(member_value, list):
                setattr(self, member_name, self.__remove_duplicates_with_order(member_value))

    def __remove_duplicates_with_order(self, value: list[Any]) -> list[Any]:
        """Remove duplicates from a list while preserving order."""
        seen = set()
        return [x for x in value if not (x in seen or seen.add(x))]  # type: ignore[func-returns-value]
