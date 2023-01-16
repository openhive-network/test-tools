import pytest

import test_tools as tt

INCORRECT_TYPES = [{}, [], (), set(), range(10), "string", None]

ASSETS_SET_FOR_MUL = [
    # multiplication by integer
    (tt.Asset.Hive(2), 0, tt.Asset.Hive(0)),
    (tt.Asset.Hive(2), 2, tt.Asset.Hive(4)),
    (tt.Asset.Hive(2), -1, tt.Asset.Hive(-2)),
    # # multiplication by float
    (tt.Asset.Hive(2), 0.5, tt.Asset.Hive(1)),
    (tt.Asset.Hive(2), -0.5, tt.Asset.Hive(-1)),
    (tt.Asset.Hive(2), 1.5, tt.Asset.Hive(3)),
    (tt.Asset.Hive(2), 0.1, tt.Asset.Hive(0.2)),
    (tt.Asset.Hive(1), 0.001, tt.Asset.Hive(0.001)),
    (tt.Asset.Hive(1), 0.0004, tt.Asset.Hive(0)),
    (tt.Asset.Hive(1), 0.0005, tt.Asset.Hive(0)),
    (tt.Asset.Hive(1), 0.0006, tt.Asset.Hive(0)),
    (tt.Asset.Hive(0.1), 0.2, tt.Asset.Hive(0.02)),
    (tt.Asset.Hive(0.001), 0.1, tt.Asset.Hive(0)),
    (tt.Asset.Hive(0.001), 0.5, tt.Asset.Hive(0)),
    (tt.Asset.Hive(0.001), 0.6, tt.Asset.Hive(0)),
]

ASSETS_SET_FOR_DIV = [
    # division by integer
    (tt.Asset.Hive(0.1), 1, tt.Asset.Hive(0.1)),
    (tt.Asset.Hive(0.01), 1, tt.Asset.Hive(0.01)),
    (tt.Asset.Hive(0.001), 1, tt.Asset.Hive(0.001)),
    (tt.Asset.Hive(0.0001), 1, tt.Asset.Hive(0)),
    (tt.Asset.Hive(0.0004), 1, tt.Asset.Hive(0)),
    (tt.Asset.Hive(0.0005), 1, tt.Asset.Hive(0)),
    (tt.Asset.Hive(1), 1_000, tt.Asset.Hive(0.001)),
    (tt.Asset.Hive(1), 4_000, tt.Asset.Hive(0)),
    (tt.Asset.Hive(1), 10_000, tt.Asset.Hive(0)),
    (tt.Asset.Hive(5), 10_000, tt.Asset.Hive(0)),  # 0.0005 HIVE out of precision
    (tt.Asset.Hive(4), 2, tt.Asset.Hive(2)),
    (tt.Asset.Hive(4.5), 3, tt.Asset.Hive(1.5)),
    (tt.Asset.Hive(6), 10_000, tt.Asset.Hive(0)),  # 0.0006 HIVE out of precision
    (tt.Asset.Hive(10), 3, tt.Asset.Hive(3.333)),
    (tt.Asset.Hive(999), 1_000, tt.Asset.Hive(0.999)),
    # division by float
    (tt.Asset.Hive(1), 1, tt.Asset.Hive(1)),
    (tt.Asset.Hive(1), 0.1, tt.Asset.Hive(10)),
    (tt.Asset.Hive(1), 0.01, tt.Asset.Hive(100)),
    (tt.Asset.Hive(1), 0.001, tt.Asset.Hive(1_000)),
]


@pytest.mark.parametrize("asset, multiplier, product", ASSETS_SET_FOR_MUL)
def test__mul__operator(asset, multiplier, product):
    assert asset * multiplier == product


@pytest.mark.parametrize("asset, multiplier, product", ASSETS_SET_FOR_MUL)
def test__rmul__operator(asset, multiplier, product):
    assert multiplier * asset == product


@pytest.mark.parametrize("asset, multiplier, product", ASSETS_SET_FOR_MUL)
def test__imul__operator(asset, multiplier, product):
    asset *= multiplier
    assert asset == product


@pytest.mark.parametrize("asset, divisor, quotient", ASSETS_SET_FOR_DIV)
def test__truediv__operator(asset, divisor, quotient):
    assert asset / divisor == quotient


@pytest.mark.parametrize("asset, dividend, quotient", ASSETS_SET_FOR_DIV)
def test__rtruediv__operator(asset, dividend, quotient):
    assert dividend / asset == quotient


@pytest.mark.parametrize("asset, divisor, quotient", ASSETS_SET_FOR_DIV)
def test__itruediv__operator(asset, divisor, quotient):
    asset /= divisor
    assert asset == quotient


@pytest.mark.parametrize(
    "dividend, divisor",
    [
        (0, tt.Asset.Hive(2)),
        (tt.Asset.Hive(2), 0),
    ],
)
def test_division_by_zero(dividend, divisor):
    with pytest.raises(ZeroDivisionError):
        dividend / divisor  # pylint: disable=pointless-statement


@pytest.mark.parametrize(
    "first_asset, second_asset",
    [
        (tt.Asset.Hive(1), tt.Asset.Hive(1)),
        (tt.Asset.Hive(1), tt.Asset.Vest(1)),
    ],
)
def test_multiplication_of_asset_by_asset(first_asset, second_asset):
    with pytest.raises(TypeError):
        first_asset * second_asset  # pylint: disable=pointless-statement


def test_inplace_multiplication_of_asset_by_asset():
    with pytest.raises(TypeError):
        asset = tt.Asset.Hive(1)
        asset *= tt.Asset.Hive(1)


@pytest.mark.parametrize(
    "first_asset, second_asset",
    [
        (tt.Asset.Hive(1), tt.Asset.Hive(1)),
        (tt.Asset.Hive(1), tt.Asset.Vest(1)),
    ],
)
def test_division_of_asset_by_asset(first_asset, second_asset):
    with pytest.raises(TypeError):
        first_asset / second_asset  # pylint: disable=pointless-statement


def test_inplace_division_of_asset_by_asset():
    with pytest.raises(TypeError):
        asset = tt.Asset.Hive(1)
        asset /= tt.Asset.Hive(1)
