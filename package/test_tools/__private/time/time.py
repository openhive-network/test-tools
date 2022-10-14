from datetime import datetime, timedelta, timezone
from typing import Final, Optional


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

    @staticmethod
    def now(time_zone: Optional[timezone] = timezone.utc) -> datetime:
        return datetime.now(time_zone)
