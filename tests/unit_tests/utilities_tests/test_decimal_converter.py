from typing import Union
import warnings

import pytest

from test_tools.__private.utilities.decimal_converter import DecimalConverter


def test_addition_when_using_converter():
    assert str(DecimalConverter.convert(0.1) + DecimalConverter.convert(0.2)) == "0.3"


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0"),
        (0.0, "0"),
        ("0.00000", "0"),
        (0.1, "0.1"),
        (".1", "0.1"),
        (1, "1"),
        (1.0, "1"),
        ("1.000", "1"),
        (1.1234, "1.1234"),
        ("1.1234", "1.1234"),
    ],
)
def test_converting_without_precision_set(value: Union[int, float, str], expected: str):
    assert str(DecimalConverter.convert(value)) == expected


@pytest.mark.parametrize(
    "value, precision, expected",
    [
        (0, 0, "0"),
        (0, 1, "0"),
        (0.123, 0, "0"),
        (0.123456789, 5, "0.12346"),
        (".123456789", 5, "0.12346"),
        (0.123454789, 5, "0.12345"),
        (".123454789", 5, "0.12345"),
    ],
)
def test_converting_with_precision_set(value: Union[int, float, str], precision: int, expected: str):
    assert str(DecimalConverter.convert(value, precision=precision)) == expected


def test_if_exception_is_raised_when_converting_with_negative_precision():
    with pytest.raises(ValueError):
        DecimalConverter.convert(1.1234, precision=-1)


def test_if_warning_is_raised_when_precision_is_lost_during_conversion():
    with pytest.warns(UserWarning):
        DecimalConverter.convert(0.1234, precision=3)


def test_if_no_warning_is_raised_when_precision_is_not_lost_during_conversion():
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("error")
        DecimalConverter.convert(0.1234, precision=4)
