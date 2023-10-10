from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from test_tools.__private.paths_to_executables import _PathsToExecutables

    from tests.unit_tests.paths_to_executables_tests.executable_init_params import ExecutableInitParams


def test_command_line_arguments_paths(paths: _PathsToExecutables, executables: list[ExecutableInitParams]) -> None:
    for executable in executables:
        path_to_executable = Path(executable.path)
        path_to_executable.touch()
        paths.parse_command_line_arguments([executable.argument, executable.path])
        assert paths.get_path_of(executable.name) == path_to_executable


def test_build_root_command_line_argument(
    paths: _PathsToExecutables, executables: list[ExecutableInitParams], prepare_build_like_dir: Path
) -> None:
    paths.parse_command_line_arguments([paths.BUILD_ROOT_PATH_COMMAND_LINE_ARGUMENT, prepare_build_like_dir.as_posix()])
    for executable in executables:
        assert paths.get_path_of(executable.name) == prepare_build_like_dir / executable.default_relative_path
