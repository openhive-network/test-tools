from datetime import timedelta

import pytest

import test_tools as tt


@pytest.mark.parametrize(
    'created, expected',
    [
        pytest.param(tt.Time.seconds(5), timedelta(seconds=5), id='seconds'),
        pytest.param(tt.Time.minutes(1), timedelta(minutes=1), id='minutes'),
        pytest.param(tt.Time.hours(100), timedelta(hours=100), id='hours'),
        pytest.param(tt.Time.days(1000), timedelta(days=1000), id='days'),
    ],
)
def test_timedelta_creation(created, expected):
    assert created == expected
