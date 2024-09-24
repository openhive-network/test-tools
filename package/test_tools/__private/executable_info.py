from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from test_tools.__private import paths_to_executables

if TYPE_CHECKING:
    from pathlib import Path

ExecutableAvailableNames = Literal["hived", "cli_wallet", "get_dev_key", "compress_block_log", "block_log_util"]


class ExecutableInfo:
    def __init__(self, executable_name: ExecutableAvailableNames) -> None:
        self.__executable_name: ExecutableAvailableNames = executable_name
        self.__path: Path | None = None

    def get_path(self) -> Path:
        return paths_to_executables.get_path_of(self.executable_name) if self.__path is None else self.__path

    def set_path(self, path: Path) -> None:
        self.__path = path

    @property
    def executable_name(self) -> ExecutableAvailableNames:
        return self.__executable_name
