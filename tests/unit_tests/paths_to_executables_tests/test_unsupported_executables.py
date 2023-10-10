from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import test_tools as tt

if TYPE_CHECKING:
    from test_tools.__private.paths_to_executables import _PathsToExecutables


def test_get_unsupported_executable(paths: _PathsToExecutables) -> None:
    with pytest.raises(tt.exceptions.NotSupportedError):
        paths.get_path_of("unsupported_executable")


def test_set_unsupported_executable(paths: _PathsToExecutables) -> None:
    with pytest.raises(tt.exceptions.NotSupportedError):
        paths.set_path_of("unsupported_executable", "path")
