from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from test_tools.__private.paths_to_executables import _PathsToExecutables

    from tests.unit_tests.paths_to_executables_tests.executable_init_params import ExecutableInitParams


def test_paths_set_manually(paths: _PathsToExecutables, executables: list[ExecutableInitParams]) -> None:
    with TemporaryDirectory() as temp_dir:
        for executable in executables:
            (executable_path := (Path(temp_dir) / executable.name)).touch()
            paths.set_path_of(executable.name, executable_path)
            assert paths.get_path_of(executable.name) == executable_path
