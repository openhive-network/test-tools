from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from beekeepy.handle.runnable import ArgumentT, AutoCloser, ConfigT
from beekeepy.handle.runnable import Executable as AbstractExecutable

if TYPE_CHECKING:
    from loguru import Logger

    from test_tools.__private.executable_info import ExecutableInfo


class Process(AbstractExecutable[ConfigT, ArgumentT]):
    def __init__(self, directory: Path | str, executable: ExecutableInfo, logger: Logger) -> None:
        self.__executable = executable
        super().__init__(executable_path=self.__executable.get_path(), working_directory=Path(directory), logger=logger)

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
            environ.update()

        return self._run(blocking=blocking, environ=environ, propagate_sigint=propagate_sigint)
