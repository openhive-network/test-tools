import test_tools as tt


def test_time_serialization_in_default_format():
    time = tt.Time.parse('1970-01-01T00:00:00')
    assert tt.Time.serialize(time) == '1970-01-01T00:00:00'


def test_parsing_time_in_custom_format():
    time = tt.Time.parse('1970-01-01T00:00:00')
    assert tt.Time.serialize(time, format_=tt.Time.TIME_OFFSET_FORMAT) == '@1970-01-01 00:00:00'
