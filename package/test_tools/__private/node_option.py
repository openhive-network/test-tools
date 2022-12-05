from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class NodeOption:
    @dataclass
    class Value:
        multiple_allowed: bool
        composed: bool
        value_type: str
        default_value: Union[str, list[str]]

    name: str
    description: str
    required: bool
    value: Optional[Value]

    @classmethod
    def from_dict(cls, data: dict) -> NodeOption:
        return cls(
            data["name"],
            data["description"],
            data["required"],
            cls.Value(
                data["value"]["multiple_allowed"],
                data["value"]["composed"],
                data["value"]["value_type"],
                data["value"]["default_value"],
            )
            if data["value"] is not None
            else None,
        )
