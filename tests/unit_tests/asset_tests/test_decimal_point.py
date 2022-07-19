import pytest
import test_tools as tt


def test_warning_about_losing_precision():
    with pytest.warns(UserWarning):
        tt.Asset.Hive(0.0001)
