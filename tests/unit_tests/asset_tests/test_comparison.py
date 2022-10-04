from __future__ import annotations

from itertools import combinations, product
from typing import List

import pytest

import test_tools as tt

AMOUNT_SET_FIRST_LESS_THAN_SECOND = [
    # VEST
    (tt.Asset.Vest(1), tt.Asset.Vest(2)),
    (tt.Asset.Vest(1), '2.000000 VESTS'),
    (tt.Asset.Vest(1), tt.Asset.Vest(2).as_nai()),
    # TESTS
    (tt.Asset.Test(1), tt.Asset.Test(2)),
    (tt.Asset.Test(1), '2.000 TESTS'),
    (tt.Asset.Test(1), tt.Asset.Test(2).as_nai()),
    # TBDS
    (tt.Asset.Tbd(1), tt.Asset.Tbd(2)),
    (tt.Asset.Tbd(1), '2.000 TBD'),
    (tt.Asset.Tbd(1), tt.Asset.Tbd(2).as_nai()),
    # HIVE
    (tt.Asset.Hive(1), tt.Asset.Hive(2)),
    (tt.Asset.Hive(1), '2.000 HIVE'),
    (tt.Asset.Hive(1), tt.Asset.Hive(2).as_nai()),
    # HBD
    (tt.Asset.Hbd(1), tt.Asset.Hbd(2)),
    (tt.Asset.Hbd(1), '2.000 HBD'),
    (tt.Asset.Hbd(1), tt.Asset.Hbd(2).as_nai()),
]

AMOUNT_SET_FIRST_GREATER_THAN_SECOND = [
    # VEST
    (tt.Asset.Vest(2), tt.Asset.Vest(1)),
    (tt.Asset.Vest(2), '1.000000 VESTS'),
    (tt.Asset.Vest(2), tt.Asset.Vest(1).as_nai()),
    # TESTS
    (tt.Asset.Test(2), tt.Asset.Test(1)),
    (tt.Asset.Test(2), '1.000 TESTS'),
    (tt.Asset.Test(2), tt.Asset.Test(1).as_nai()),
    # TBD
    (tt.Asset.Tbd(2), tt.Asset.Tbd(1)),
    (tt.Asset.Tbd(2), '1.000 TBD'),
    (tt.Asset.Tbd(2), tt.Asset.Tbd(1).as_nai()),
    # HIVE
    (tt.Asset.Hive(2), tt.Asset.Hive(1)),
    (tt.Asset.Hive(2), '1.000 HIVE'),
    (tt.Asset.Hive(2), tt.Asset.Hive(1).as_nai()),
    # HBD
    (tt.Asset.Hbd(2), tt.Asset.Hbd(1)),
    (tt.Asset.Hbd(2), '1.000 HBD'),
    (tt.Asset.Hbd(2), tt.Asset.Hbd(1).as_nai()),
]

AMOUNT_SET_FIRST_EQUAL_SECOND = [
    # VEST
    (tt.Asset.Vest(1), tt.Asset.Vest(1)),
    (tt.Asset.Vest(1), '1.000000 VESTS'),
    (tt.Asset.Vest(1), tt.Asset.Vest(1).as_nai()),
    # TESTS
    (tt.Asset.Test(1), tt.Asset.Test(1)),
    (tt.Asset.Test(1), '1.000 TESTS'),
    (tt.Asset.Test(1), tt.Asset.Test(1).as_nai()),
    # TBD
    (tt.Asset.Tbd(1), tt.Asset.Tbd(1)),
    (tt.Asset.Tbd(1), '1.000 TBD'),
    (tt.Asset.Tbd(1), tt.Asset.Tbd(1).as_nai()),
    # HIVE
    (tt.Asset.Hive(1), tt.Asset.Hive(1)),
    (tt.Asset.Hive(1), '1.000 HIVE'),
    (tt.Asset.Hive(1), tt.Asset.Hive(1).as_nai()),
    # HBD
    (tt.Asset.Hbd(1), tt.Asset.Hbd(1)),
    (tt.Asset.Hbd(1), '1.000 HBD'),
    (tt.Asset.Hbd(1), tt.Asset.Hbd(1).as_nai()),
]


def combine_asset_amount_with_different_asset_type(asset_amount: tt.AnyAsset, string_or_dict: str) -> List:
    def _return_list_with_different_amounts_string_type(asset_amount: tt.AnyAsset) -> List:
        assets_as_string = ['1.000 TESTS', '1.000 TBD', '1.000 HIVE', '1.000000 VESTS', '1.000 HBD']
        return [x for x in assets_as_string if asset_amount.token not in x]

    def _return_list_with_different_amounts_dict_type(asset_amount: tt.AnyAsset) -> List:
        assets_as_dict = [tt.Asset.Vest(1).as_nai(), tt.Asset.Test(1).as_nai(), tt.Asset.Hive(1).as_nai(),
                          tt.Asset.Tbd(1).as_nai(), tt.Asset.Hbd(1).as_nai()]
        return [asset_dict for asset_dict in assets_as_dict if asset_amount.nai not in asset_dict['nai']]

    if string_or_dict == 'string':
        return list(product([asset_amount], _return_list_with_different_amounts_string_type(asset_amount)))
    if string_or_dict == 'dict':
        return list(product([asset_amount], _return_list_with_different_amounts_dict_type(asset_amount)))


SET_WITH_SECOND_STRING_VALUE_AND_NOT_MATCHING_TOKENS = [
    *combine_asset_amount_with_different_asset_type(tt.Asset.Vest(1), 'string'),
    *combine_asset_amount_with_different_asset_type(tt.Asset.Test(1), 'string'),
    *combine_asset_amount_with_different_asset_type(tt.Asset.Hbd(1), 'string'),
    *combine_asset_amount_with_different_asset_type(tt.Asset.Tbd(1), 'string'),
    *combine_asset_amount_with_different_asset_type(tt.Asset.Hive(1), 'string'),
]

SET_WITH_SECOND_NAI_VALUE_AND_NOT_MATCHING_KEYS = [
    *combine_asset_amount_with_different_asset_type(tt.Asset.Vest(1), 'dict'),
    *combine_asset_amount_with_different_asset_type(tt.Asset.Test(1), 'dict'),
    *combine_asset_amount_with_different_asset_type(tt.Asset.Hbd(1), 'dict'),
    *combine_asset_amount_with_different_asset_type(tt.Asset.Tbd(1), 'dict'),
    *combine_asset_amount_with_different_asset_type(tt.Asset.Hive(1), 'dict'),
]


@pytest.mark.parametrize(
    'first_amount, second_amount', AMOUNT_SET_FIRST_EQUAL_SECOND
)
def test__eq__operator(first_amount, second_amount):
    assert first_amount == second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', AMOUNT_SET_FIRST_LESS_THAN_SECOND
)
def test__lt__operator(first_amount, second_amount):
    assert first_amount < second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', AMOUNT_SET_FIRST_GREATER_THAN_SECOND
)
def test__gt__operator(first_amount, second_amount):
    assert first_amount > second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', AMOUNT_SET_FIRST_LESS_THAN_SECOND + AMOUNT_SET_FIRST_EQUAL_SECOND

)
def test__le__operator(first_amount, second_amount):
    assert first_amount <= second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', AMOUNT_SET_FIRST_GREATER_THAN_SECOND + AMOUNT_SET_FIRST_EQUAL_SECOND
)
def test__ge__operator(first_amount, second_amount):
    assert first_amount >= second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', AMOUNT_SET_FIRST_GREATER_THAN_SECOND + AMOUNT_SET_FIRST_LESS_THAN_SECOND
)
def test_negative__eq__operator(first_amount, second_amount):
    assert not first_amount == second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', AMOUNT_SET_FIRST_GREATER_THAN_SECOND + AMOUNT_SET_FIRST_EQUAL_SECOND
)
def test_negative__lt__operator(first_amount, second_amount):
    assert not first_amount < second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', AMOUNT_SET_FIRST_LESS_THAN_SECOND + AMOUNT_SET_FIRST_EQUAL_SECOND
)
def test_negative__gt__operator(first_amount, second_amount):
    assert not first_amount > second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', AMOUNT_SET_FIRST_GREATER_THAN_SECOND

)
def test_negative__le__operator(first_amount, second_amount):
    assert not first_amount <= second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', AMOUNT_SET_FIRST_LESS_THAN_SECOND
)
def test_negative__ge__operator(first_amount, second_amount):
    assert not first_amount >= second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', SET_WITH_SECOND_NAI_VALUE_AND_NOT_MATCHING_KEYS
)
def test_eq_operator_with_invalid_nai_amount(first_amount, second_amount):
    with pytest.raises(TypeError):
        assert first_amount == second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', SET_WITH_SECOND_NAI_VALUE_AND_NOT_MATCHING_KEYS
)
def test_lt_operator_with_invalid_nai_amount(first_amount, second_amount):
    with pytest.raises(TypeError):
        assert first_amount < second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', SET_WITH_SECOND_NAI_VALUE_AND_NOT_MATCHING_KEYS
)
def test_le_operator_with_invalid_nai_amount(first_amount, second_amount):
    with pytest.raises(TypeError):
        assert first_amount <= second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', SET_WITH_SECOND_NAI_VALUE_AND_NOT_MATCHING_KEYS
)
def test_gt_operator_with_invalid_nai_amount(first_amount, second_amount):
    with pytest.raises(TypeError):
        assert first_amount > second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', SET_WITH_SECOND_NAI_VALUE_AND_NOT_MATCHING_KEYS
)
def test_ge_operator_with_invalid_nai_amount(first_amount, second_amount):
    with pytest.raises(TypeError):
        assert first_amount >= second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', SET_WITH_SECOND_STRING_VALUE_AND_NOT_MATCHING_TOKENS
)
def test_eq_operator_with_invalid_string_amount(first_amount, second_amount):
    with pytest.raises(TypeError):
        assert first_amount == second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', SET_WITH_SECOND_STRING_VALUE_AND_NOT_MATCHING_TOKENS
)
def test_lt_operator_with_with_invalid_string_amount(first_amount, second_amount):
    with pytest.raises(TypeError):
        assert first_amount < second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', SET_WITH_SECOND_STRING_VALUE_AND_NOT_MATCHING_TOKENS
)
def test_le_operator_with_with_invalid_string_amount(first_amount, second_amount):
    with pytest.raises(TypeError):
        assert first_amount <= second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', SET_WITH_SECOND_STRING_VALUE_AND_NOT_MATCHING_TOKENS
)
def test_gt_operator_with_with_invalid_string_amount(first_amount, second_amount):
    with pytest.raises(TypeError):
        assert first_amount > second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount', SET_WITH_SECOND_STRING_VALUE_AND_NOT_MATCHING_TOKENS
)
def test_ge_operator_with_with_invalid_string_amount(first_amount, second_amount):
    with pytest.raises(TypeError):
        assert first_amount >= second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount',
    list(combinations((tt.Asset.Vest(1), tt.Asset.Test(1), tt.Asset.Hive(1), tt.Asset.Hbd(1), tt.Asset.Tbd(1)), 2))
)
def test_eq_operator_with_mixed_asset_types(first_amount, second_amount):
    with pytest.raises(TypeError):
        assert first_amount == second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount',
    list(combinations((tt.Asset.Vest(1), tt.Asset.Test(1), tt.Asset.Hive(1), tt.Asset.Hbd(1), tt.Asset.Tbd(1)), 2))
)
def test_lt_operator_with_mixed_asset_types(first_amount, second_amount):
    with pytest.raises(TypeError):
        assert first_amount < second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount',
    list(combinations((tt.Asset.Vest(1), tt.Asset.Test(1), tt.Asset.Hive(1), tt.Asset.Hbd(1), tt.Asset.Tbd(1)), 2))
)
def test_le_operator_with_mixed_asset_types(first_amount, second_amount):
    with pytest.raises(TypeError):
        assert first_amount <= second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount',
    list(combinations((tt.Asset.Vest(1), tt.Asset.Test(1), tt.Asset.Hive(1), tt.Asset.Hbd(1), tt.Asset.Tbd(1)), 2))
)
def test_gt_operator_with_mixed_asset_types(first_amount, second_amount):
    with pytest.raises(TypeError):
        assert first_amount > second_amount


@pytest.mark.parametrize(
    'first_amount, second_amount',
    list(combinations((tt.Asset.Vest(1), tt.Asset.Test(1), tt.Asset.Hive(1), tt.Asset.Hbd(1), tt.Asset.Tbd(1)), 2))
)
def test_ge_operator_with_mixed_asset_types(first_amount, second_amount):
    with pytest.raises(TypeError):
        assert first_amount >= second_amount
