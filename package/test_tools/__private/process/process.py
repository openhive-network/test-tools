from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from helpy._executable.executable import ArgumentT, AutoCloser, ConfigT
from helpy._executable.executable import Executable as HelpyExecutable
from test_tools.__private.utilities.fake_time import configure_fake_time

if TYPE_CHECKING:

    from loguru import Logger

    from test_tools.__private.executable_info import ExecutableInfo




class Process(HelpyExecutable[ConfigT, ArgumentT]):
    def __init__(self, directory: Path | str, executable: ExecutableInfo, logger: Logger) -> None:
        self.__executable = executable
        super().__init__(
            executable_path=self.__executable.get_path(),
            working_directory=Path(directory),
            logger=logger
        )

    @property
    def executable_info(self) -> ExecutableInfo:
        return self.__executable

    def run(
        self,
        *,
        blocking: bool,
        propagate_sigint: bool = False,
        with_arguments: ArgumentT | None = None,  # noqa: ARG002
        with_environment_variables: dict[str, str] | None = None,
        with_time_control: str | None = None,
    ) -> AutoCloser:
        environ = with_environment_variables or {}
        if with_time_control:
            environ.update(configure_fake_time(self._logger, with_time_control))

        return self._run(
            blocking=blocking,
            environ=environ,
            propagate_sigint=propagate_sigint
        )

