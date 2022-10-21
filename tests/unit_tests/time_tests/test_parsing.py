from datetime import datetime, timezone

import pytest

import test_tools as tt
from test_tools.__private.exceptions import ParseError


@pytest.mark.parametrize(
    "time, expected",
    [
        ("1970-01-01T00:00:00", datetime(1970, 1, 1, tzinfo=timezone.utc)),
        ("1970-01-01T00:00:00.250", datetime(1970, 1, 1, microsecond=250000, tzinfo=timezone.utc)),
    ],
    ids=("default_format", "default_format_including_millis"),
)
def test_parsing_time_in_default_formats(time: str, expected: datetime):
    assert tt.Time.parse(time) == expected


def test_parsing_time_in_custom_format():
    assert tt.Time.parse("01.01.1970", format_="%d.%m.%Y") == datetime(1970, 1, 1, tzinfo=timezone.utc)


def test_parsing_invalid_time_in_default_formats():
    time = "01.01.1970"

    with pytest.raises(ParseError) as exception:
        assert tt.Time.parse(time)
    assert (
        f"Could not be parse the `{time}` string using the "
        f"`{tt.Time.DEFAULT_FORMAT}` or `{tt.Time.DEFAULT_FORMAT_WITH_MILLIS}` default formats" in str(exception.value)
    )


def test_parsing_time_in_invalid_custom_format():
    time = "01.01.1970"
    invalid_format = "invalid_format"

    with pytest.raises(ParseError) as exception:
        assert tt.Time.parse(time, format_=invalid_format)
    assert f"Could not be parse the `{time}` string using the `{invalid_format}` custom format" in str(exception.value)
