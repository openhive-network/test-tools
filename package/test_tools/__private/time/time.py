from datetime import datetime, timedelta, timezone
from typing import Final, Optional

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

    @staticmethod
    def now(time_zone: Optional[timezone] = timezone.utc) -> datetime:
        return datetime.now(time_zone)
