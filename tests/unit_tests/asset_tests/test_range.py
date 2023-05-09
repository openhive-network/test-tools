import pytest

import test_tools as tt


@pytest.mark.parametrize(
    "lower_limit, upper_limit",
    [
        (tt.Asset.Test(1), tt.Asset.Test(2)),
        (tt.Asset.Tbd(1), tt.Asset.Tbd(2)),
        (tt.Asset.Vest(1), tt.Asset.Vest(2)),
        (tt.Asset.Hive(1), tt.Asset.Hive(2)),
        (tt.Asset.Hbd(1), tt.Asset.Hbd(2)),
    ]
)
def test_correct_lower_limit_and_upper_limit_arguments(lower_limit, upper_limit):
    tt.Asset.Range(lower_limit, upper_limit)


@pytest.mark.parametrize("percentage_range,", [1, 10, 1000, 100_000])
def test_correct_type_of_arguments_in_percentage_range_argument(percentage_range):
    tt.Asset.Range(tt.Asset.Test(1), percentage_range=percentage_range)


@pytest.mark.parametrize("percentage_range,", [None, False, {}, [], (), set(), -3, 3.14, "string", range(0, 1)])
def test_incorrect_type_of_arguments_in_percentage_range_argument(percentage_range):
    with pytest.raises(AssertionError):
        tt.Asset.Range(tt.Asset.Test(1), percentage_range=percentage_range)


def test_simultaneously_using_upper_limit_and_percentage_range_arguments():
    with pytest.raises(AssertionError):
        tt.Asset.Range(tt.Asset.Test(1), tt.Asset.Test(2), percentage_range=5)


def test_different_types_of_assets_during_create_range_asset_object():
    with pytest.raises(AssertionError):
        tt.Asset.Range(tt.Asset.Test(1), tt.Asset.Vest(2))


@pytest.mark.parametrize(
    "upper_limit,"
    "lower_limit",
    [
        (tt.Asset.Test(1), None),
        (tt.Asset.Test(1), None),
        (tt.Asset.Test(1), True),
        (tt.Asset.Test(1), False),
        (tt.Asset.Test(1), {}),
        (tt.Asset.Test(1), []),
        (tt.Asset.Test(1), ()),
        (tt.Asset.Test(1), set()),
        (tt.Asset.Test(1), 3),
        (tt.Asset.Test(1), 3.14),
        (tt.Asset.Test(1), "string"),
        (tt.Asset.Test(1), range(0, 1)),

        (None, tt.Asset.Test(1)),
        (True, tt.Asset.Test(1)),
        (False, tt.Asset.Test(1)),
        ({}, tt.Asset.Test(1)),
        ([], tt.Asset.Test(1)),
        ((), tt.Asset.Test(1)),
        (set(), tt.Asset.Test(1)),
        (3, tt.Asset.Test(1)),
        (3.14, tt.Asset.Test(1)),
        ("string", tt.Asset.Test(1)),
        (range(0, 1), tt.Asset.Test(1)),
    ]
)
def test_incorrect_type_of_arguments_in_lower_and_upper_limit(upper_limit, lower_limit):
    with pytest.raises(AssertionError):
        tt.Asset.Range(lower_limit, upper_limit)


def test_if_the_upper_limit_is_greater_than_the_lower_limit():
    with pytest.raises(AssertionError) as exception:
        tt.Asset.Range(tt.Asset.Test(3), tt.Asset.Test(1))

    error_message = exception.value.args[0]
    assert "The upper limit cannot be greater than the lower limit" in error_message


def test_if_the_upper_limit_is_the_same_as_the_lower_limit():
    with pytest.raises(AssertionError) as exception:
        tt.Asset.Range(tt.Asset.Test(1), tt.Asset.Test(1))

    error_message = exception.value.args[0]
    assert "The upper limit cannot be greater than the lower limit" in error_message


def test_banned_way_to_creating_a_asset_range_object_without_specifying_arguments():
    with pytest.raises(TypeError):
        tt.Asset.Range()
