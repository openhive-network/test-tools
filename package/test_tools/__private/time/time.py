from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from os import PathLike
    from typing import Final, Optional, Union


class Time:
    DEFAULT_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%S"
    DEFAULT_FORMAT_WITH_MILLIS: Final[str] = "%Y-%m-%dT%H:%M:%S.%f"
    TIME_OFFSET_FORMAT: Final[str] = "@%Y-%m-%d %H:%M:%S.%f"

    def __new__(cls, *_args, **_kwargs):
        raise TypeError(f"Creation object of {Time.__name__} class is forbidden.")

    @staticmethod
    def parse(time: str, *, format_: str = DEFAULT_FORMAT) -> datetime:
        return datetime.strptime(time, format_)

    @staticmethod
    def serialize(time: datetime, *, format_: str = DEFAULT_FORMAT) -> str:
        return datetime.strftime(time, format_)

    @staticmethod
    def milliseconds(milliseconds: float) -> timedelta:
        return timedelta(milliseconds=milliseconds)

    @staticmethod
    def seconds(amount: float) -> timedelta:
        return timedelta(seconds=amount)

    @staticmethod
    def minutes(amount: float) -> timedelta:
        return timedelta(minutes=amount)

    @staticmethod
    def hours(amount: float) -> timedelta:
        return timedelta(hours=amount)

    @staticmethod
    def days(amount: float) -> timedelta:
        return timedelta(days=amount)

    @classmethod
    def are_close(cls, first: datetime, second: datetime, *, absolute_tolerance: Optional[timedelta] = None) -> bool:
        if absolute_tolerance is None:
            absolute_tolerance = cls.seconds(0)

        return abs(first - second) <= absolute_tolerance

    @classmethod
    def save_to_file(cls, file_path: Union[str, PathLike], time: datetime, *, format_: str = DEFAULT_FORMAT) -> None:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(cls.serialize(time, format_=format_))

    @classmethod
    def read_from_file(
        cls, file_path: Union[str, bytes, PathLike], *, format_: str = TIME_OFFSET_FORMAT, offset: Optional[timedelta] = None
    ) -> str:
        if offset is None:
            offset = cls.seconds(0)

        with open(file_path, encoding="utf-8") as file:
            time_string = file.read().strip()

        if "." not in time_string:
            time_string += ".0"

        time = cls.parse(time_string, format_=cls.DEFAULT_FORMAT_WITH_MILLIS) + offset

        return cls.serialize(time, format_=format_)
