from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from test_tools.__private.paths_to_executables import Priority

if TYPE_CHECKING:
    from test_tools.__private.paths_to_executables import _PathsToExecutables

    from tests.unit_tests.paths_to_executables_tests.executable_init_params import ExecutableInitParams


def test_paths_of_installed_executables(paths: _PathsToExecutables, executables: list[ExecutableInitParams]) -> None:
    with TemporaryDirectory() as temp_path:
        build_path = Path(temp_path)
        for executable in executables:
            (executable_path := (build_path / executable.path)).parent.mkdir(parents=True, exist_ok=True)
            executable_path.touch()
            paths.debug_set_path_of(executable_name=executable.name, executable_path=None, priority=Priority.NOT_SET)
            paths.set_installed_executables({executable.name: executable_path})
            assert paths.get_path_of(executable.name) == executable_path
