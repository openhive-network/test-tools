from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar, get_args

from schemas.base import convert
from schemas.fields.resolvables import Resolvable

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


if TYPE_CHECKING:
    StringQuoted = str
    PathQuoted = Path
else:

    class StringQuoted(str, Resolvable["StringQuoted", str]):
        @staticmethod
        def resolve(incoming_cls: type, value: str) -> StringQuoted:  # noqa: ARG004
            if len(value) == 0 or value == '""':
                return StringQuoted()
            return StringQuoted(value.strip('"'))

        def serialize(self) -> Any:
            return f'"{self}"'

    class PathQuoted(Path, Resolvable["PathQuoted", str]):
        @staticmethod
        def resolve(incoming_cls: type, value: str) -> PathQuoted:  # type: ignore[override]  # noqa: ARG004
            if len(value) == 0 or value == '""':
                return PathQuoted()
            return PathQuoted(value.strip('"'))

        def serialize(self) -> Any:
            return f'"{self.as_posix()}"'


T = TypeVar("T")


class UniqueList(list[T], Resolvable["UniqueList[T]", list[T]], Generic[T]):
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

    @staticmethod
    def resolve(incoming_cls: type, value: list[T]) -> UniqueList[T]:
        if len(value) == 0:
            return UniqueList()
        non_empty_str_t = get_args(incoming_cls)[0]
        return UniqueList(convert(value, type=list[non_empty_str_t]))  # type: ignore[valid-type]

    def serialize(self) -> Any:
        return list(self)
