from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from test_tools.__private.paths_to_executables import _PathsToExecutables

    from tests.unit_tests.paths_to_executables_tests.executable_init_params import ExecutableInitParams


@pytest.fixture(autouse=True, scope="module")
def prepare_paths() -> None:
    for path in [
        Path("path_set_manually"),
        Path("path_set_from_command_line_arguments"),
        Path("path_set_from_environment_variables"),
        Path("path_of_installed_executable"),
    ]:
        path.touch()


def test_manually_set_path_priority(paths: _PathsToExecutables, executable: ExecutableInitParams) -> None:
    paths.set_path_of(executable.name, "path_set_manually")
    paths.parse_command_line_arguments([executable.argument, "path_set_from_command_line_arguments"])
    paths.set_environment_variables({executable.environment_variable: "path_set_from_environment_variables"})
    paths.set_installed_executables({executable.name: "path_of_installed_executable"})

    assert paths.get_path_of(executable.name) == Path("path_set_manually")


def test_path_from_command_line_argument_priority(paths: _PathsToExecutables, executable: ExecutableInitParams) -> None:
    paths.parse_command_line_arguments([executable.argument, "path_set_from_command_line_arguments"])
    paths.set_environment_variables({executable.environment_variable: "path_set_from_environment_variables"})
    paths.set_installed_executables({executable.name: "path_of_installed_executable"})

    assert paths.get_path_of(executable.name) == Path("path_set_from_command_line_arguments")


def test_path_from_environment_variables_priority(paths: _PathsToExecutables, executable: ExecutableInitParams) -> None:
    paths.set_environment_variables({executable.environment_variable: "path_set_from_environment_variables"})
    paths.set_installed_executables({executable.name: "path_of_installed_executable"})

    assert paths.get_path_of(executable.name) == Path("path_set_from_environment_variables")
