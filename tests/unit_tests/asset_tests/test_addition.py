import pytest

import test_tools as tt


def test_addition_of_same_tokens():
    first = tt.Asset.Hive(2)
    second = tt.Asset.Hive(2)
    result = first + second

    assert first == second == tt.Asset.Hive(2)  # Addends aren't modified
    assert result == tt.Asset.Hive(4)
    assert isinstance(result, tt.Asset.Hive)


def test_addition_of_different_tokens():
    with pytest.raises(TypeError):
        _ = tt.Asset.Hive(2) + tt.Asset.Test(2)


def test_addition_and_assignment_of_same_tokens():
    first = tt.Asset.Hive(2)
    second = tt.Asset.Hive(2)
    first += second

    assert first == tt.Asset.Hive(4)
    assert second == tt.Asset.Hive(2)  # Addend isn't modified


def test_addition_and_assignment_of_different_tokens():
    first = tt.Asset.Hive(2)
    second = tt.Asset.Test(2)

    with pytest.raises(TypeError):
        first += second
