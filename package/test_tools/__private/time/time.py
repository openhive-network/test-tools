from datetime import datetime, timedelta, timezone
import math
import time
from typing import Callable, Final, Optional, Union

from dateutil.relativedelta import relativedelta

from test_tools.__private.exceptions import ParseError


class Time:
    DEFAULT_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%S"
    DEFAULT_FORMAT_WITH_MILLIS: Final[str] = "%Y-%m-%dT%H:%M:%S.%f"
    TIME_OFFSET_FORMAT: Final[str] = "@%Y-%m-%d %H:%M:%S.%f"

    def __new__(cls, *_args, **_kwargs):
        raise TypeError(f"Creation object of {Time.__name__} class is forbidden.")

    @classmethod
    def parse(
        cls, time: str, *, format_: Optional[str] = None, time_zone: Optional[timezone] = timezone.utc
    ) -> datetime:
        """
        By default, when `format_` parameter is specified as None - the ISO format (tt.Time.DEFAULT_FORMAT)
        and ISO format including milliseconds (tt.Time.DEFAULT_FORMAT_WITH_MILLIS) could be parsed.
        """

        def __parse_in_specified_format(_format: str) -> datetime:
            try:
                parsed = datetime.strptime(time, _format)
                return parsed.replace(tzinfo=time_zone) if time_zone else parsed
            except ValueError as exception:
                format_info = (
                    f"`{_format}` custom format."
                    if _format is not cls.DEFAULT_FORMAT_WITH_MILLIS
                    else f"`{cls.DEFAULT_FORMAT}` or `{cls.DEFAULT_FORMAT_WITH_MILLIS}` default formats."
                )
                raise ParseError(f"Could not be parse the `{time}` string using the {format_info}") from exception

        if format_ is not None:
            return __parse_in_specified_format(format_)

        try:
            return __parse_in_specified_format(cls.DEFAULT_FORMAT)
        except ParseError:
            return __parse_in_specified_format(cls.DEFAULT_FORMAT_WITH_MILLIS)

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

    @staticmethod
    def weeks(amount: float) -> timedelta:
        return timedelta(days=amount * 7)

    @staticmethod
    def months(amount: int) -> relativedelta:
        return relativedelta(months=amount)

    @staticmethod
    def years(amount: int) -> relativedelta:
        return relativedelta(years=amount)

    @classmethod
    def are_close(cls, first: datetime, second: datetime, *, absolute_tolerance: Optional[timedelta] = None) -> bool:
        if absolute_tolerance is None:
            absolute_tolerance = cls.seconds(0)

        try:
            return abs(first - second) <= absolute_tolerance
        except TypeError as exception:
            raise ValueError(
                "The time zones of the two dates differ.\n"
                "Note, that time zones can be modified (e.g.: `.replace(tzinfo=datetime.timezone.utc)`)."
            ) from exception

    @classmethod
    def now(
        cls,
        *,
        time_zone: Optional[timezone] = timezone.utc,
        serialize: bool = True,
        serialize_format: str = DEFAULT_FORMAT,
    ) -> Union[str, datetime]:
        time = datetime.now(time_zone)
        return cls.serialize(time, format_=serialize_format) if serialize else time

    @classmethod
    def from_now(
        cls,
        *,
        milliseconds: int = 0,
        seconds: int = 0,
        minutes: int = 0,
        hours: int = 0,
        days: int = 0,
        weeks: int = 0,
        months: int = 0,
        years: int = 0,
        time_zone: Optional[timezone] = timezone.utc,
        serialize: bool = True,
        serialize_format: str = DEFAULT_FORMAT,
    ) -> Union[str, datetime]:
        if not any([milliseconds, seconds, minutes, hours, days, weeks, months, years]):
            raise ValueError(
                "At least one keyword argument is required.\n"
                "If you want to get the current datetime, please use `tt.Time.now()` instead."
            )

        delta = relativedelta(
            microseconds=milliseconds * 10**3,
            seconds=seconds,
            minutes=minutes,
            hours=hours,
            days=days,
            weeks=weeks,
            months=months,
            years=years,
        )

        time = cls.now(time_zone=time_zone, serialize=False) + delta
        return cls.serialize(time, format_=serialize_format) if serialize else time

    @staticmethod
    def wait_for(
        predicate: Callable[[], bool],
        *,
        timeout: float = math.inf,
        timeout_error_message: Optional[str] = None,
        poll_time: float = 1.0,
    ) -> float:
        assert timeout >= 0

        already_waited = 0
        while not predicate():
            if timeout - already_waited <= 0:
                raise TimeoutError(timeout_error_message or "Waited too long, timeout was reached")

            sleep_time = min(poll_time, timeout)
            time.sleep(sleep_time)
            already_waited += sleep_time

        return already_waited
