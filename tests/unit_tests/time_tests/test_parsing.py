from datetime import datetime

import test_tools as tt


def test_parsing_time_in_default_format():
    assert tt.Time.parse("1970-01-01T00:00:00") == datetime.strptime("1970-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")


def test_parsing_time_in_custom_format():
    assert tt.Time.parse("01.01.1970", format_="%d.%m.%Y") == datetime.strptime("01.01.1970", "%d.%m.%Y")
