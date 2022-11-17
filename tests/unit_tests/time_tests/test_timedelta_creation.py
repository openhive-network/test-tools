from datetime import timedelta

from dateutil.relativedelta import relativedelta
import pytest

import test_tools as tt


@pytest.mark.parametrize(
    "created, expected",
    [
        pytest.param((tt.Time.milliseconds(5)), timedelta(milliseconds=5), id="milliseconds"),
        pytest.param(tt.Time.seconds(5), timedelta(seconds=5), id="seconds"),
        pytest.param(tt.Time.minutes(1), timedelta(minutes=1), id="minutes"),
        pytest.param(tt.Time.hours(100), timedelta(hours=100), id="hours"),
        pytest.param(tt.Time.days(1000), timedelta(days=1000), id="days"),
        pytest.param(tt.Time.weeks(1000), timedelta(weeks=1000), id="weeks"),
        pytest.param(tt.Time.months(1000), relativedelta(months=1000), id="months"),
        pytest.param(tt.Time.years(1000), relativedelta(years=1000), id="years"),
    ],
)
def test_timedelta_creation(created, expected):
    assert created == expected
