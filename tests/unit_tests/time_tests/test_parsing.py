from datetime import datetime, timezone

import test_tools as tt


def test_parsing_time_in_default_format():
    time = "1970-01-01T00:00:00"
    format_ = "%Y-%m-%dT%H:%M:%S"

    assert tt.Time.parse(time) == datetime.strptime(time, format_).replace(tzinfo=timezone.utc)


def test_parsing_time_in_custom_format():
    time = "01.01.1970"
    format_ = "%d.%m.%Y"

    assert tt.Time.parse(time, format_=format_) == datetime.strptime(time, format_).replace(tzinfo=timezone.utc)
