import pytest

import test_tools as tt


@pytest.mark.parametrize(
    "asset, lower_limit, upper_limit",
    [
        (tt.Asset.Test(2), tt.Asset.Test(1), tt.Asset.Test(3)),
        (tt.Asset.Tbd(2), tt.Asset.Tbd(1), tt.Asset.Tbd(3)),
        (tt.Asset.Vest(2), tt.Asset.Vest(1), tt.Asset.Vest(3)),
        (tt.Asset.Hive(2), tt.Asset.Hive(1), tt.Asset.Hive(3)),
        (tt.Asset.Hbd(2), tt.Asset.Hbd(1), tt.Asset.Hbd(3)),
    ],
)
def test_correct_type_as_asset_to_check_in_range(asset, lower_limit, upper_limit):
    assert asset in tt.Asset.Range(lower_limit, upper_limit)


@pytest.mark.parametrize("asset", [tt.Asset.Test(1), tt.Asset.Test(1.099)])
def test_the_percentage_range_of_the_given_asset(asset):
    assert asset in tt.Asset.Range(tt.Asset.Test(1), percentage_range=10)


@pytest.mark.parametrize("asset", [tt.Asset.Test(1.1), tt.Asset.Test(0.999)])
def test_the_boundary_conditions_of_the_given_asset(asset):
    with pytest.raises(AssertionError):
        assert asset in tt.Asset.Range(tt.Asset.Test(1), percentage_range=10)


@pytest.mark.parametrize("build_in_types", [None, True, False, {}, [], (), set(), 3, 3.14, "string", range(0, 1)])
def test_give_incorrect_type_as_asset_to_check_in_range(build_in_types):
    with pytest.raises(AssertionError):
        assert build_in_types in tt.Asset.Range(tt.Asset.Test(1), tt.Asset.Test(2))
