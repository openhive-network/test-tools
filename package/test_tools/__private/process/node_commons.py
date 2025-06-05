from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypeVar

if TYPE_CHECKING:
    from typing_extensions import Self

if TYPE_CHECKING:
    BacktraceAllowedValues = Literal["yes", "no"]
    SinkAllowedValues = Literal["STDERR", "STDOUT", "WLOG", "ELOG", "DLOG", "ILOG"]
    ReportTypes = Literal["NONE", "MINIMAL", "REGULAR", "FULL"]
else:
    BacktraceAllowedValues = str
    SinkAllowedValues = str
    ReportTypes = str


class QuotedMarker:
    """Following string will be serialized with quotes and will be deserialized without them."""


StringQuoted = str | QuotedMarker
PathQuoted = Path | QuotedMarker
T = TypeVar("T")


class UniqueList(list[T]):
    def __init__(self, _obj: Iterable[T] | T = []) -> None:  # noqa: B006
        super().__init__(set(_obj) if isinstance(_obj, Iterable) else [_obj])
        self.sort()

    def append(self, __object: T) -> None:
        if __object not in self:
            super().append(__object)
            self.sort()

    def extend(self, __iterable: Iterable[T]) -> None:
        outcome = {*self, *__iterable}
        self.clear()
        super().extend(outcome)
        self.sort()

    def __iadd__(self, _: Any) -> Self:  # type: ignore[override]
        raise NotImplementedError

    def __add__(self, _: Any) -> Self:  # type: ignore[override]
        raise NotImplementedError
