from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from test_tools.__private.exceptions import NotSupportedError

if TYPE_CHECKING:
    from test_tools.__private.paths_to_executables import _PathsToExecutables

    from tests.unit_tests.paths_to_executables_tests.executable_init_params import ExecutableInitParams


def test_missing_paths(paths: _PathsToExecutables, executables: list[ExecutableInitParams]) -> None:
    for executable in executables:
        with pytest.raises(NotSupportedError):
            paths.get_path_of(executable.name + "_malformed")
