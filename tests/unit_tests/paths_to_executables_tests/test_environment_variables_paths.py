from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from test_tools.__private.paths_to_executables import BUILD_ROOT_PATH_ENVIRONMENT_VARIABLE

if TYPE_CHECKING:
    from test_tools.__private.paths_to_executables import _PathsToExecutables

    from tests.unit_tests.paths_to_executables_tests.executable_init_params import ExecutableInitParams


def test_environment_variables_paths(paths: _PathsToExecutables, executables: list[ExecutableInitParams]) -> None:
    for executable in executables:
        executable_path = Path(executable.path)
        executable_path.touch()
        paths.set_environment_variables({executable.environment_variable: executable.path})
        assert paths.get_path_of(executable.name) == executable_path


def test_build_root_environment_variable(
    paths: _PathsToExecutables, executables: list[ExecutableInitParams], prepare_build_like_dir: Path
) -> None:
    paths.set_environment_variables({BUILD_ROOT_PATH_ENVIRONMENT_VARIABLE: prepare_build_like_dir.as_posix()})
    for executable in executables:
        assert paths.get_path_of(executable.name) == prepare_build_like_dir / executable.default_relative_path
