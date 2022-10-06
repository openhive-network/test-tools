from __future__ import annotations

from abc import ABC
from typing import Generic, TypeVar

T = TypeVar("T")


class Handle(ABC, Generic[T]):
    """Base class for all objects pointed by handles. Contains handle by which is pointed."""

    def __init__(self, *args, implementation: T, **kwargs):
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self._implementation = implementation

    def __str__(self) -> str:
        return str(self._implementation)

    def __repr__(self) -> str:
        return repr(self._implementation)
