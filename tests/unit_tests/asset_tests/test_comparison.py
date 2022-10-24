from __future__ import annotations

import pytest

import test_tools as tt

ASSETS_SET_FIRST_LESS_THAN_SECOND = [
    # VEST
    (tt.Asset.Vest(1), tt.Asset.Vest(2)),
    (tt.Asset.Vest(1), tt.Asset.Vest(2).as_nai()),
    # TESTS
    (tt.Asset.Test(1), tt.Asset.Test(2)),
    (tt.Asset.Test(1), tt.Asset.Test(2).as_nai()),
    # TBDS
    (tt.Asset.Tbd(1), tt.Asset.Tbd(2)),
    (tt.Asset.Tbd(1), tt.Asset.Tbd(2).as_nai()),
    # HIVE
    (tt.Asset.Hive(1), tt.Asset.Hive(2)),
    (tt.Asset.Hive(1), tt.Asset.Hive(2).as_nai()),
    # HBD
    (tt.Asset.Hbd(1), tt.Asset.Hbd(2)),
    (tt.Asset.Hbd(1), tt.Asset.Hbd(2).as_nai()),
]

ASSETS_SET_FIRST_GREATER_THAN_SECOND = [
    # VEST
    (tt.Asset.Vest(2), tt.Asset.Vest(1)),
    (tt.Asset.Vest(2), tt.Asset.Vest(1).as_nai()),
    # TESTS
    (tt.Asset.Test(2), tt.Asset.Test(1)),
    (tt.Asset.Test(2), tt.Asset.Test(1).as_nai()),
    # TBD
    (tt.Asset.Tbd(2), tt.Asset.Tbd(1)),
    (tt.Asset.Tbd(2), tt.Asset.Tbd(1).as_nai()),
    # HIVE
    (tt.Asset.Hive(2), tt.Asset.Hive(1)),
    (tt.Asset.Hive(2), tt.Asset.Hive(1).as_nai()),
    # HBD
    (tt.Asset.Hbd(2), tt.Asset.Hbd(1)),
    (tt.Asset.Hbd(2), tt.Asset.Hbd(1).as_nai()),
]

ASSETS_SET_FIRST_EQUAL_SECOND = [
    # VEST
    (tt.Asset.Vest(1), tt.Asset.Vest(1)),
    (tt.Asset.Vest(1), tt.Asset.Vest(1).as_nai()),
    # TESTS
    (tt.Asset.Test(1), tt.Asset.Test(1)),
    (tt.Asset.Test(1), tt.Asset.Test(1).as_nai()),
    # TBD
    (tt.Asset.Tbd(1), tt.Asset.Tbd(1)),
    (tt.Asset.Tbd(1), tt.Asset.Tbd(1).as_nai()),
    # HIVE
    (tt.Asset.Hive(1), tt.Asset.Hive(1)),
    (tt.Asset.Hive(1), tt.Asset.Hive(1).as_nai()),
    # HBD
    (tt.Asset.Hbd(1), tt.Asset.Hbd(1)),
    (tt.Asset.Hbd(1), tt.Asset.Hbd(1).as_nai()),
]


@pytest.mark.parametrize("first_asset, second_asset", ASSETS_SET_FIRST_EQUAL_SECOND)
def test__eq__operator(first_asset, second_asset):
    assert first_asset == second_asset


@pytest.mark.parametrize("first_asset, second_asset", ASSETS_SET_FIRST_LESS_THAN_SECOND)
def test__lt__operator(first_asset, second_asset):
    assert first_asset < second_asset


@pytest.mark.parametrize("first_asset, second_asset", ASSETS_SET_FIRST_GREATER_THAN_SECOND)
def test__gt__operator(first_asset, second_asset):
    assert first_asset > second_asset


@pytest.mark.parametrize("first_asset, second_asset", ASSETS_SET_FIRST_LESS_THAN_SECOND + ASSETS_SET_FIRST_EQUAL_SECOND)
def test__le__operator(first_asset, second_asset):
    assert first_asset <= second_asset


@pytest.mark.parametrize(
    "first_asset, second_asset", ASSETS_SET_FIRST_GREATER_THAN_SECOND + ASSETS_SET_FIRST_EQUAL_SECOND
)
def test__ge__operator(first_asset, second_asset):
    assert first_asset >= second_asset


@pytest.mark.parametrize(
    "first_asset, second_asset", ASSETS_SET_FIRST_GREATER_THAN_SECOND + ASSETS_SET_FIRST_LESS_THAN_SECOND
)
def test_negative__eq__operator(first_asset, second_asset):
    assert not first_asset == second_asset


@pytest.mark.parametrize(
    "first_asset, second_asset", ASSETS_SET_FIRST_GREATER_THAN_SECOND + ASSETS_SET_FIRST_EQUAL_SECOND
)
def test_negative__lt__operator(first_asset, second_asset):
    assert not first_asset < second_asset


@pytest.mark.parametrize("first_asset, second_asset", ASSETS_SET_FIRST_LESS_THAN_SECOND + ASSETS_SET_FIRST_EQUAL_SECOND)
def test_negative__gt__operator(first_asset, second_asset):
    assert not first_asset > second_asset


@pytest.mark.parametrize("first_asset, second_asset", ASSETS_SET_FIRST_GREATER_THAN_SECOND)
def test_negative__le__operator(first_asset, second_asset):
    assert not first_asset <= second_asset


@pytest.mark.parametrize("first_asset, second_asset", ASSETS_SET_FIRST_LESS_THAN_SECOND)
def test_negative__ge__operator(first_asset, second_asset):
    assert not first_asset >= second_asset


def test_string_asset_eq_comparison():
    assert tt.Asset.Test(1) == "1.000 TESTS"


def test_string_asset_lt_comparison():
    assert tt.Asset.Test(1) < "2.000 TESTS"


@pytest.mark.parametrize("asset", [100, [tt.Asset.Test(1)], True])
def test_asset_lt_comparison_with_value_in_incorrect_type(asset):
    with pytest.raises(TypeError):
        assert tt.Asset.Test(1) < asset


@pytest.mark.parametrize("asset", [100, [tt.Asset.Test(1)], True])
def test_asset_eq_comparison_with_value_in_incorrect_type(asset):
    with pytest.raises(TypeError):
        assert tt.Asset.Test(1) == asset


def test_dict_asset_lt_comparison_with_incorrect_keys():
    invalid_asset = {"price": "1000000", "token": 6, "value": "@@000000037"}
    with pytest.raises(TypeError):
        assert tt.Asset.Test(1) < invalid_asset


def test_dict_asset_eq_comparison_with_incorrect_keys():
    invalid_asset = {"price": "1000000", "token": 6, "value": "@@000000037"}
    with pytest.raises(TypeError):
        assert tt.Asset.Test(1) == invalid_asset


def test_dict_asset_lt_comparison_with_different_nais():
    with pytest.raises(TypeError):
        assert tt.Asset.Test(1) < tt.Asset.Hbd(2).as_nai()


def test_dict_asset_eq_comparison_with_different_nais():
    with pytest.raises(TypeError):
        assert tt.Asset.Test(1) == tt.Asset.Hbd(1).as_nai()


def test_string_asset_comparison_with_incorrect_token():
    with pytest.raises(TypeError):
        assert tt.Asset.Test(1) == "100 EUR"


def test_asset_lt_comparison_with_different_tokens():
    with pytest.raises(TypeError):
        assert tt.Asset.Test(1) < tt.Asset.Hbd(2)


def test_asset_eq_comparison_with_different_tokens():
    with pytest.raises(TypeError):
        assert tt.Asset.Test(1) == tt.Asset.Hbd(1)
