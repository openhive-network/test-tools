from __future__ import annotations

import shutil
from argparse import ArgumentParser
from enum import Enum
from os import getenv, path
from pathlib import Path

from test_tools.__private.exceptions import MissingPathToExecutableError, NotSupportedError
from test_tools.__private.utilities.tests_type import is_automatic_test

BUILD_ROOT_PATH_ENVIRONMENT_VARIABLE = "HIVE_BUILD_ROOT_PATH"


def get_configuration_hint() -> str:
    return (
        f"Edit and add following line to /etc/environment and restart computer.\n"
        f'{BUILD_ROOT_PATH_ENVIRONMENT_VARIABLE}= # Should be something like: "/home/dev/hive/build"'
    )


class Priority(Enum):
    MANUAL = 0
    CLI = 1
    ENVIRONMENT = 2
    INSTALL = 3
    _DEBUG = 98
    NOT_SET = 99


class ExecutableDetails:
    def __init__(self, name: str, default_path_from_build: Path | str | None = None) -> None:
        self.name = name
        self.argument = f'--{name.replace("_", "-")}-path'
        self.environment_variable = f"{name}_PATH".upper()
        if default_path_from_build is not None and isinstance(default_path_from_build, str):
            default_path_from_build = Path(default_path_from_build)
        self.default_path_from_build = default_path_from_build
        self.__path: Path | None = None
        self.__priority: Priority = Priority.NOT_SET

    @property
    def path(self) -> Path:
        if self.__path is None:
            raise MissingPathToExecutableError(f"Missing path to {self.name}\n" + get_configuration_hint())

        return self.__path

    def is_path_set(self) -> bool:
        return self.__path is not None

    def set_path(
        self, *, root_path: Path | None = None, full_path: Path | None = None, priority: Priority = Priority.MANUAL
    ) -> None:
        assert priority != Priority._DEBUG, "Priority cannot be set to DEBUG explicitly"
        if priority.value > self.__priority.value:
            return

        if root_path is not None:
            assert self.default_path_from_build is not None
            assert root_path.exists()
            assert root_path.is_dir()
            self.__path = root_path / self.default_path_from_build
        elif full_path is not None and full_path.exists():
            assert full_path.is_file()
            self.__path = full_path
        self.__priority = priority

    def debug_set_path(self, path: Path | None, *, priority: Priority = Priority._DEBUG) -> None:
        self.__path = path
        self.__priority = priority


class _PathsToExecutables:
    BUILD_ROOT_PATH_COMMAND_LINE_ARGUMENT = "--build-root-path"

    def __init__(self, *, skip_command_line_argument_parsing: bool = False) -> None:
        self.executables: dict[str, ExecutableDetails] = {
            "hived": ExecutableDetails("hived", "programs/hived/hived"),
            "cli_wallet": ExecutableDetails("cli_wallet", "programs/cli_wallet/cli_wallet"),
            "get_dev_key": ExecutableDetails("get_dev_key", "programs/util/get_dev_key"),
            "compress_block_log": ExecutableDetails("compress_block_log", "programs/util/compress_block_log"),
        }

        self.set_installed_executables()
        self.set_environment_variables()
        if not skip_command_line_argument_parsing:
            self.parse_command_line_arguments()

    def get_paths_in_use(self) -> dict[str, Path]:
        return {
            executable.name: executable.path for executable in self.executables.values() if executable.is_path_set()
        }

    def get_path_of(self, executable_name: str) -> Path:
        return self.__get_executable_details(executable_name).path

    def set_path_of(self, executable_name: str, executable_path: Path | str) -> None:
        self.__assert_is_supported(executable_name)
        self.executables[executable_name].set_path(
            full_path=self.__assure_path(executable_path), priority=Priority.MANUAL
        )

    def debug_set_path_of(
        self, executable_name: str, executable_path: Path | str | None, priority: Priority = Priority._DEBUG
    ) -> None:
        self.__assert_is_supported(executable_name)
        self.executables[executable_name].debug_set_path(path=self.__assure_path(executable_path), priority=priority)

    def parse_command_line_arguments(self, arguments: list[str] | None = None) -> None:
        parser = ArgumentParser()

        parser.add_argument(self.BUILD_ROOT_PATH_COMMAND_LINE_ARGUMENT, dest="build_root", type=Path)
        for executable in self.executables.values():
            parser.add_argument(executable.argument, dest=executable.name, type=Path)

        parsed = parser.parse_args(arguments)
        self.__set_paths(Priority.CLI, paths=parsed.__dict__, root=parsed.build_root)

    def set_environment_variables(self, variables: dict[str, str] | None = None) -> None:
        if variables is None:
            variables = self.__get_environment_variables_from_operating_system()

        variables = {name: path.expandvars(value) for name, value in variables.items()}
        build_root_path_from_environ_raw = variables.get(BUILD_ROOT_PATH_ENVIRONMENT_VARIABLE)
        build_root_path_from_environ: Path | None = None
        if build_root_path_from_environ_raw is not None:  # mypy checks
            build_root_path_from_environ = Path(build_root_path_from_environ_raw)
        self.__set_paths(
            Priority.ENVIRONMENT,
            paths={
                executable.name: self.__assure_path(variables.get(executable.environment_variable, None))
                for executable in self.executables.values()
            },
            root=build_root_path_from_environ,
        )

    def set_installed_executables(self, installed_executables: dict[str, Path | str] | None = None) -> None:
        if installed_executables is None:
            for executable_name, executable in self.executables.items():
                if (path_from_system := shutil.which(executable_name)) is not None:
                    executable.set_path(full_path=Path(path_from_system), priority=Priority.INSTALL)
            return

        for executable_name, executable in self.executables.items():
            if (new_path := installed_executables.get(executable_name, None)) is not None:
                executable.set_path(full_path=self.__assure_path(new_path), priority=Priority.INSTALL)

    @staticmethod
    def __append_environment_variable_value_if_defined(variables: dict[str, str], name: str) -> None:
        variable = getenv(name)
        if variable is not None:
            variables[name] = variable

    def __get_environment_variables_from_operating_system(self) -> dict[str, str]:
        variables: dict[str, str] = {}

        self.__append_environment_variable_value_if_defined(variables, BUILD_ROOT_PATH_ENVIRONMENT_VARIABLE)

        for executable in self.executables.values():
            self.__append_environment_variable_value_if_defined(variables, executable.environment_variable)

        return variables

    def __get_executable_details(self, executable_name: str) -> ExecutableDetails:
        self.__assert_is_supported(executable_name)
        return self.executables[executable_name]

    def __assert_is_supported(self, executable_name: str) -> None:
        if not self.__is_supported(executable_name):
            raise NotSupportedError(f"Executable `{executable_name}` is not supported")

    def __is_supported(self, executable_name: str) -> bool:
        return executable_name in self.executables

    def __set_paths(self, priority: Priority, paths: dict[str, Path | None], root: Path | None = None) -> None:
        for executable in self.executables.values():
            if (parsed_path := paths.get(executable.name, None)) is not None:
                executable.set_path(full_path=parsed_path, priority=priority)
            elif root is not None:
                executable.set_path(root_path=root, priority=priority)

    @classmethod
    def __assure_path(cls, path_like: Path | str | None) -> Path | None:
        if path_like is None or isinstance(path_like, Path):
            return path_like
        return Path(path_like)


__paths = _PathsToExecutables(skip_command_line_argument_parsing=is_automatic_test())


def get_path_of(executable_name: str) -> Path:
    return __paths.get_path_of(executable_name)


def set_path_of(executable_name: str, executable_path: Path) -> None:
    __paths.set_path_of(executable_name, executable_path)


def get_paths_in_use() -> dict[str, Path]:
    return __paths.get_paths_in_use()


def print_paths_in_use() -> None:
    print("\n".join(get_paths_in_use()))  # noqa: T201


def print_configuration_hint() -> None:
    print(get_configuration_hint())  # noqa: T201


def debug_set_path_of(executable_name: str, executable_path: Path | None, priority: Priority = Priority._DEBUG) -> None:
    __paths.debug_set_path_of(executable_name, executable_path, priority)
