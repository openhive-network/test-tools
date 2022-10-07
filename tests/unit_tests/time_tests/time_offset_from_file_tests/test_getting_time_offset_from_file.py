from __future__ import annotations

import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

import test_tools as tt

if TYPE_CHECKING:
    from datetime import timedelta
    from typing import Final

TIMESTAMP_FILE_PATH: Final[Path] = Path(__file__).parent / "timestamp"


def test_getting_time_offset_from_file():
    # ACT
    time_offset = tt.Time.read_from_file(TIMESTAMP_FILE_PATH)

    # ASSERT
    assert time_offset == "@2022-10-07 10:16:20.000000"


@pytest.mark.parametrize(
    "offset, expected",
    [
        (tt.Time.seconds(10), "@2022-10-07 10:16:30.000000"),
        (tt.Time.hours(-10), "@2022-10-07 00:16:20.000000"),
    ],
)
def test_getting_modified_time_offset_from_file(offset: timedelta, expected: str):
    # ACT
    time_offset = tt.Time.read_from_file(TIMESTAMP_FILE_PATH, offset=offset)

    # ASSERT
    assert time_offset == expected


def test_getting_time_offset_from_file_when_saved_with_default_format():
    # ARRANGE
    time = datetime.datetime(2022, 10, 7, 10, 16, 20, 123456)

    # ACT
    tt.Time.save_to_file(TIMESTAMP_FILE_PATH, time)

    # ASSERT
    assert tt.Time.read_from_file(TIMESTAMP_FILE_PATH) == "@2022-10-07 10:16:20.000000"
