import test_tools as tt


def test_comparison_without_tolerance():
    time = tt.Time.parse('1970-01-01T00:00:00')

    assert tt.Time.are_close(time, time)
    assert not tt.Time.are_close(time, time + tt.Time.seconds(1))


def test_comparison_with_absolute_tolerance():
    time = tt.Time.parse('1970-01-01T00:00:00')

    assert tt.Time.are_close(time, time - tt.Time.seconds(6), absolute_tolerance=tt.Time.seconds(5)) is False
    assert tt.Time.are_close(time, time - tt.Time.seconds(5), absolute_tolerance=tt.Time.seconds(5)) is True
    assert tt.Time.are_close(time, time - tt.Time.seconds(4), absolute_tolerance=tt.Time.seconds(5)) is True

    assert tt.Time.are_close(time, time + tt.Time.seconds(4), absolute_tolerance=tt.Time.seconds(5)) is True
    assert tt.Time.are_close(time, time + tt.Time.seconds(5), absolute_tolerance=tt.Time.seconds(5)) is True
    assert tt.Time.are_close(time, time + tt.Time.seconds(6), absolute_tolerance=tt.Time.seconds(5)) is False
