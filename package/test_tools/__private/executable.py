from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING, Any, Literal, get_args

from test_tools.__private import paths_to_executables

if TYPE_CHECKING:
    from pathlib import Path

ExecutableAvailableNames = Literal["hived", "cli_wallet", "get_dev_key", "compress_block_log", "block_log_util"]
NodeTypesReturnType = Literal["testnet", "mirrornet", "mainnet"]
NodeTypes: tuple[str, str, str] = get_args(NodeTypesReturnType)


class Executable:
    def __init__(self, executable_name: ExecutableAvailableNames) -> None:
        self.__executable_name = executable_name
        self.__path: Path | None = None

    def get_path(self) -> Path:
        return paths_to_executables.get_path_of(self.executable_name) if self.__path is None else self.__path

    def set_path(self, path: Path) -> None:
        self.__path = path

    @property
    def executable_name(self) -> ExecutableAvailableNames:
        return self.__executable_name

    @property
    def build_version(self) -> NodeTypesReturnType:
        node_type = self.get_version()["version"]["node_type"]
        assert isinstance(node_type, str)
        assert node_type in NodeTypes
        return node_type  # type: ignore[return-value]

    def get_build_commit_hash(self) -> str:
        hive_revision = self.get_version()["version"]["hive_revision"]
        assert isinstance(hive_revision, str)
        return hive_revision

    def get_version(self) -> dict[str, Any]:
        assert self.executable_name == "hived", "version can only be checked for hived binary!"
        result = json.loads(self.__run_and_get_output("--version"))
        assert isinstance(result, dict)
        return result

    def __run_and_get_output(self, *arguments: str) -> str:
        result = subprocess.check_output(
            [str(self.get_path()), *arguments],
            stderr=subprocess.STDOUT,
        )

        return result.decode("utf-8").strip()

    def get_supported_plugins(self) -> list[str]:
        output = self.__run_and_get_output("--list-plugins")
        return output.split("\n")
