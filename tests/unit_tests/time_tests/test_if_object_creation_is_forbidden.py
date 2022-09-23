import pytest

import test_tools as tt


def test_if_object_creation_is_forbidden():
    with pytest.raises(TypeError):
        tt.Time()
