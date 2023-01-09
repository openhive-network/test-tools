from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class NodeOption:
    @dataclass
    class Value:
        required: bool
        multitoken: bool
        composed: bool
        value_type: str
        default_value: Union[str, list[str]]

    name: str
    description: str
    value: Optional[Value]

    @classmethod
    def from_dict(cls, data: dict) -> NodeOption:
        return cls(
            data["name"],
            data["description"],
            cls.Value(
                data["value"]["required"],
                data["value"]["multitoken"],
                data["value"]["composed"],
                data["value"]["value_type"],
                data["value"]["default_value"],
            )
            if data["value"] is not None
            else None,
        )
