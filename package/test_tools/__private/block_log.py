from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import typing
from typing import Literal, NoReturn, Optional, Union

from test_tools.__private import paths_to_executables
from test_tools.__private.exceptions import MissingBlockLogArtifactsError
from test_tools.__private.logger.logger_internal_interface import logger
from test_tools.__private.scope import context


class BlockLog:
    def __init__(self, path: Union[Path, str]):
        self.__name = context.names.register_numbered_name(self.__class__.__name__)
        self.__logger = logger.create_child_logger(self.__name)

        self.__path = Path(path)
        self.__assert_path_exists()

        self.__logger.info(f"Created with path reference to: {self.__path}")

    def __repr__(self):
        return f"<BlockLog: path={self.__path}>"

    @property
    def path(self) -> Path:
        return self.__path

    @property
    def artifacts_path(self) -> Path:
        return self.path.with_suffix(".artifacts")

    @property
    def length(self) -> int:
        output = subprocess.check_output(
            [paths_to_executables.get_path_of("block_log_util"), "get-head-block-number", self.__path],
            encoding="utf-8",
        )
        return int(output)

    def copy_to(
        self,
        destination: Union[Path, str],
        *,
        artifacts: Literal["required", "optional", "excluded"] = "excluded",
    ) -> BlockLog:
        """
        Copies block log and its artifacts (if requested via `artifacts` parameter) to specified `destination`. By
        default, only block log is copied and artifacts are excluded.

        It is unsafe to copy block log or use it for replay when node, which is source if block log, is run. It might
        lead to problems, because files referenced by block log object might be modified at the same time by its owner.

        :param destination: Path to existing directory, where block log (and optionally artifacts) will be copied or
            path to destination block log file, which should be created when copy will be performed. Second option can
            be used to change name of destination block log.
        :param artifacts: Decides how artifacts are handled during block log copying. Allowed values:
            - "required" -- Artifacts are always copied. Missing artifacts are treated as error.
            - "optional" -- Artifacts are copied if exists. This is not a problem when artifacts are missing.
            - "excluded" -- Artifacts are never copied.
        :return: Copy of source block log.
        """
        assert self.__path.exists()
        destination = Path(destination)

        # Assert that `artifacts` parameter have allowed value, defined in its type hint.
        artifacts_type_hint = typing.get_type_hints(self.copy_to)["artifacts"]
        artifacts_allowed_values = typing.get_args(artifacts_type_hint)
        if artifacts not in artifacts_allowed_values:
            raise ValueError(f"{artifacts=}, but supported values are: {', '.join(artifacts_allowed_values)}.")

        if artifacts != "excluded":
            if self.artifacts_path.exists():
                shutil.copy(
                    self.artifacts_path,
                    destination if destination.is_dir() else destination.with_suffix(".artifacts"),
                )
            elif artifacts == "required":
                self.__raise_missing_artifacts_error(self.artifacts_path)
            else:
                assert artifacts == "optional"

        copied_block_log_path = shutil.copy(self.__path, destination)
        return BlockLog(copied_block_log_path)

    def truncate(self, output_directory: Union[Path, str], block_number: int) -> BlockLog:
        """
        Shorten block log to `block_number` blocks and stores result in `output_directory` as:
        - `output_directory` / block_log,
        - `output_directory` / block_log.artifacts.

        :param output_directory: In this directory truncated `block_log` and `block_log.artifacts` will be stored.
        :param block_number: Limit number of blocks in the output block log.
        :return: Truncated block log.
        """
        subprocess.run(
            [
                paths_to_executables.get_path_of("compress_block_log"),
                f"--input-block-log={self.__path.parent.absolute()}",
                f"--output-block-log={Path(output_directory).absolute()}",
                f"--block-count={block_number}",
                "--decompress",
            ],
            check=True,
        )
        return BlockLog(output_directory / "block_log")

    @staticmethod
    def __raise_missing_artifacts_error(block_log_artifacts_path) -> NoReturn:
        raise MissingBlockLogArtifactsError(
            f"Block log artifacts with following path are missing:\n{block_log_artifacts_path}"
        )

    def __assert_path_exists(self) -> Optional[NoReturn]:
        if not self.__path.exists():
            raise FileNotFoundError(f"Following path does not exists: {self.__path}")
