import random

import pytest

import test_tools as tt


@pytest.mark.parametrize(
    "interval", ["milliseconds", "seconds", "minutes", "hours", "days", "weeks", "months", "years"]
)
def test_from_now_with_parameters(interval: str):
    # ARRANGE
    value = 0
    while value == 0:
        value = random.randint(-1000, 1000)
    interval_container = {interval: value}
    delta = getattr(tt.Time, interval)(value)

    # ACT
    shifted_time = tt.Time.from_now(**interval_container, serialize_format=tt.Time.DEFAULT_FORMAT_WITH_MILLIS)

    # ASSERT
    reference_time_in_from_now = tt.Time.parse(shifted_time) - delta
    assert reference_time_in_from_now < tt.Time.now(serialize=False)


def test_from_now_without_argument():
    with pytest.raises(ValueError):
        tt.Time.from_now()
