from datetime import datetime, timedelta
from typing import Final


class Time:
    DEFAULT_FORMAT: Final[str] = '%Y-%m-%dT%H:%M:%S'

    def __new__(cls, *_args, **_kwargs):
        raise TypeError(f'Creation object of {Time.__name__} class is forbidden.')

    @staticmethod
    def parse(time: str, *, format_: str = DEFAULT_FORMAT) -> datetime:
        return datetime.strptime(time, format_)

    @staticmethod
    def seconds(amount: int) -> timedelta:
        return timedelta(seconds=amount)

    @staticmethod
    def minutes(amount: int) -> timedelta:
        return timedelta(minutes=amount)

    @staticmethod
    def hours(amount: int) -> timedelta:
        return timedelta(hours=amount)

    @staticmethod
    def days(amount: int) -> timedelta:
        return timedelta(days=amount)
