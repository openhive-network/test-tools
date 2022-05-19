import pytest

import test_tools as tt


def test_get_unsupported_executable(paths):
    with pytest.raises(tt.exceptions.NotSupported):
        paths.get_path_of('unsupported_executable')


def test_set_unsupported_executable(paths):
    with pytest.raises(tt.exceptions.NotSupported):
        paths.set_path_of('unsupported_executable', 'path')
