from __future__ import annotations

import pytest

import test_tools as tt

ASSETS_SET_FOR_ADD = [
    # VEST
    (tt.Asset.Vest(1), tt.Asset.Vest(2), tt.Asset.Vest(3)),
    (tt.Asset.Vest(1), tt.Asset.Vest(2).as_nai(), tt.Asset.Vest(3)),
    # TESTS
    (tt.Asset.Test(1), tt.Asset.Test(2), tt.Asset.Test(3)),
    (tt.Asset.Test(1), tt.Asset.Test(2).as_nai(), tt.Asset.Test(3)),
    # TBDS
    (tt.Asset.Tbd(1), tt.Asset.Tbd(2), tt.Asset.Tbd(3)),
    (tt.Asset.Tbd(1), tt.Asset.Tbd(2).as_nai(), tt.Asset.Tbd(3)),
    # HIVE
    (tt.Asset.Hive(1), tt.Asset.Hive(2), tt.Asset.Hive(3)),
    (tt.Asset.Hive(1), tt.Asset.Hive(2).as_nai(), tt.Asset.Hive(3)),
    # HBD
    (tt.Asset.Hbd(1), tt.Asset.Hbd(2), tt.Asset.Hbd(3)),
    (tt.Asset.Hbd(1), tt.Asset.Hbd(2).as_nai(), tt.Asset.Hbd(3)),
]

ASSETS_SET_FOR_SUB = [
    # VEST
    (tt.Asset.Vest(3), tt.Asset.Vest(2), tt.Asset.Vest(1)),
    (tt.Asset.Vest(3), tt.Asset.Vest(2).as_nai(), tt.Asset.Vest(1)),
    # TESTS
    (tt.Asset.Test(3), tt.Asset.Test(2), tt.Asset.Test(1)),
    (tt.Asset.Test(3), tt.Asset.Test(2).as_nai(), tt.Asset.Test(1)),
    # TBDS
    (tt.Asset.Tbd(3), tt.Asset.Tbd(2), tt.Asset.Tbd(1)),
    (tt.Asset.Tbd(3), tt.Asset.Tbd(2).as_nai(), tt.Asset.Tbd(1)),
    # HIVE
    (tt.Asset.Hive(3), tt.Asset.Hive(2), tt.Asset.Hive(1)),
    (tt.Asset.Hive(3), tt.Asset.Hive(2).as_nai(), tt.Asset.Hive(1)),
    # HBD
    (tt.Asset.Hbd(3), tt.Asset.Hbd(2), tt.Asset.Hbd(1)),
    (tt.Asset.Hbd(3), tt.Asset.Hbd(2).as_nai(), tt.Asset.Hbd(1)),
]


@pytest.mark.parametrize("first_asset, second_asset, third_asset", ASSETS_SET_FOR_ADD)
def test__add__operator(first_asset, second_asset, third_asset):
    assert first_asset + second_asset == third_asset


@pytest.mark.parametrize("first_asset, second_asset, third_asset", ASSETS_SET_FOR_ADD)
def test__iadd__operator(first_asset, second_asset, third_asset):
    first_asset += second_asset
    assert first_asset == third_asset


@pytest.mark.parametrize("first_asset, second_asset, third_asset", ASSETS_SET_FOR_SUB)
def test__sub__operator(first_asset, second_asset, third_asset):
    assert first_asset - second_asset == third_asset


@pytest.mark.parametrize("first_asset, second_asset, third_asset", ASSETS_SET_FOR_SUB)
def test__isub__operator(first_asset, second_asset, third_asset):
    first_asset -= second_asset
    assert first_asset == third_asset


def test_add_string_asset():
    assert tt.Asset.Test(1) + "2.000 TESTS" == tt.Asset.Test(3)


@pytest.mark.parametrize("asset", [100, [tt.Asset.Test(1)], True])
def test_add_asset_with_value_in_incorrect_type(asset):
    with pytest.raises(TypeError):
        assert tt.Asset.Test(1) + asset


def test_add_dict_asset_with_incorrect_keys():
    invalid_asset = {"price": "2000000", "token": 6, "value": "@@000000037"}
    with pytest.raises(TypeError):
        assert tt.Asset.Test(1) + invalid_asset == tt.Asset.Test(3)


def test_add_dict_asset_with_different_nais():
    with pytest.raises(TypeError):
        assert tt.Asset.Test(1) + tt.Asset.Hbd(2).as_nai() == tt.Asset.Test(3)


def test_add_string_asset_with_incorrect_token():
    with pytest.raises(TypeError):
        assert tt.Asset.Test(1) + "2 EUR" == tt.Asset.Test(3)


def test_add_asset_with_different_token():
    with pytest.raises(TypeError):
        assert tt.Asset.Test(1) + tt.Asset.Hbd(2) == tt.Asset.Test(3)
