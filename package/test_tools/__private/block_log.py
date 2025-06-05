from __future__ import annotations

import contextlib
import json
import shutil
import subprocess
import typing
from pathlib import Path
from typing import ClassVar, Final, Literal, overload

import msgspec

from schemas.apis.block_api.fundaments_of_responses import (
    BlockLogUtilSignedBlockBaseTransaction,
    BlockLogUtilSignedBlockBaseTransactionLegacy,
)
from test_tools.__private import paths_to_executables
from test_tools.__private.exceptions import BlockLogError, BlockLogUtilError, MissingBlockLogArtifactsError
from wax.helpy._interfaces.time import Time, TimeFormats

if typing.TYPE_CHECKING:
    from datetime import datetime

BlockLogUtilResultTransaction = BlockLogUtilSignedBlockBaseTransaction
BlockLogUtilResultTransactionLegacy = BlockLogUtilSignedBlockBaseTransactionLegacy


class BlockLog:
    MONO_BLOCK_FILE_NAME: ClassVar[str] = "block_log"
    MONO_ARTIFACTS_FILE_NAME: ClassVar[str] = "block_log.artifacts"
    SPLIT_BLOCK_FILES_PATTERN: ClassVar[str] = "block_log_part.????"
    SPLIT_ARTIFACT_FILES_PATTERN: ClassVar[str] = "*.????.artifacts"

    def __init__(self, path: Path | str, mode: Literal["monolithic", "split", "auto"] = "auto") -> None:
        self.__path = Path(path)
        if not self.__path.is_dir():
            raise BlockLogError(f"{self.__path} is not a directory as required")

        if mode == "auto":
            self.__is_split = self.__auto_determine_mode()
        else:
            self.__is_split = mode == "split"

    def __auto_determine_mode(self) -> bool:
        """Determine which 'split' mode to use based on files existence."""
        split_files = BlockLog.get_existing_block_files(True, self.__path)
        mono_log_exists = (self.__path / self.MONO_BLOCK_FILE_NAME).exists()

        if not mono_log_exists and not split_files:
            raise BlockLogError(
                f"Can't use auto mode. Neither single nor split log files found in the directory of {self.__path}."
            )

        return bool(split_files)

    def __repr__(self) -> str:
        return f"<BlockLog: path={self.__path}, is_split={self.__is_split}>"

    @property
    def path(self) -> Path:
        return self.__path

    @property
    def is_split(self) -> bool:
        return self.__is_split

    @staticmethod
    def get_existing_block_files(split_files: bool, from_dir: Path) -> list[Path]:
        if split_files:
            return sorted(from_dir.glob(BlockLog.SPLIT_BLOCK_FILES_PATTERN))

        mono_log_path = from_dir / BlockLog.MONO_BLOCK_FILE_NAME
        if mono_log_path.exists():
            return [mono_log_path]

        return []  # no files found

    @staticmethod
    def get_existing_artifact_files(split_files: bool, from_dir: Path) -> list[Path]:
        if split_files:
            return sorted(from_dir.glob(BlockLog.SPLIT_ARTIFACT_FILES_PATTERN))

        mono_artifacts_path = from_dir / BlockLog.MONO_ARTIFACTS_FILE_NAME
        if mono_artifacts_path.exists():
            return [mono_artifacts_path]

        return []  # no files found

    @property
    def block_files(self) -> list[Path]:
        """Returns an entire list of blocklog files (many in split mode)."""
        return BlockLog.get_existing_block_files(self.__is_split, self.__path)

    def __block_files_force(self) -> list[Path]:
        the_files: list[Path] = self.block_files
        if not the_files:
            raise BlockLogError(f"No log files found on {self.__path} for is_split={self.__is_split} configuration")
        return the_files

    @property
    def artifact_files(self) -> list[Path]:
        return BlockLog.get_existing_artifact_files(self.__is_split, self.__path)

    def copy_to(
        self,
        destination: Path | str,
        *,
        artifacts: Literal["required", "optional", "excluded"] = "excluded",
    ) -> BlockLog:
        """
        Copies block log and its artifacts (if requested via `artifacts` parameter) to specified `destination`.

        By default, only block log is copied and artifacts are excluded.

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
        assert self.__path.exists(), f"Given block log path of '{self.__path}' does not exist."
        destination = Path(destination)
        destination = destination if destination.is_dir() else destination.parent

        # Assert that `artifacts` parameter have allowed value, defined in its type hint.
        artifacts_type_hint = typing.get_type_hints(self.copy_to)["artifacts"]
        artifacts_allowed_values = typing.get_args(artifacts_type_hint)
        if artifacts not in artifacts_allowed_values:
            raise ValueError(f"{artifacts=}, but supported values are: {', '.join(artifacts_allowed_values)}.")

        if artifacts != "excluded":
            file_list = self.artifact_files
            if file_list:
                for file in file_list:
                    if not self.__same_copying_destination(file, destination):
                        shutil.copy(file, destination)
            elif artifacts == "required":
                self.__raise_missing_artifacts_error(self.path)
            else:
                assert artifacts == "optional"

        for file in self.block_files:
            if not self.__same_copying_destination(file, destination):
                shutil.copy(file, destination)
        return BlockLog(destination, "split" if self.__is_split else "monolithic")

    def __same_copying_destination(self, file: Path, destination: Path) -> bool:
        return file.parent.resolve() == destination.resolve()

    def truncate(self, output_directory: Path | str, block_number: int) -> BlockLog:
        """
        Shorten block log to `block_number` blocks and stores result in `output_directory` as.

            - `output_directory` / block_log,
            - `output_directory` / block_log.artifacts.

        :param output_directory: In this directory truncated `block_log` and `block_log.artifacts` will be stored.
        :param block_number: Limit number of blocks in the output block log.
        :return: Truncated block log.
        """
        copied = self.copy_to(Path(output_directory))
        for file in reversed(copied.block_files):
            process = subprocess.run(
                [
                    paths_to_executables.get_path_of("block_log_util"),
                    f"--block-log={Path(file).absolute()}",
                    f"--block-number={block_number}",
                    "--truncate",
                    "--force",
                ],
                check=False,
            )
            if process.returncode == 0:
                return BlockLog(Path(output_directory), "split" if self.__is_split else "monolithic")

            file.unlink()

        split_str = "split" if self.__is_split else "monolithic"
        raise BlockLogUtilError(f"No file of {split_str} block log in {self.__path} could be sussessfully truncated.")

    def __run_and_get_output(self, *args: str) -> str:
        process = subprocess.run(
            [paths_to_executables.get_path_of("block_log_util"), *args], capture_output=True, check=False
        )

        if process.returncode:
            raise BlockLogUtilError(
                f"stdout: {process.stdout.decode().strip()}\n\nstderr: {process.stderr.decode().strip()}"
            )
        return process.stdout.decode().strip()

    def generate_artifacts(self) -> None:
        """Generate artifacts file(s)."""
        file_list = self.block_files
        for file in file_list:
            block_log_arg = ["--block-log", str(file)]
            self.__run_and_get_output("--generate-artifacts", *block_log_arg)

    def get_head_block_number(self) -> int:
        """
        Get number of head block in block_log.

        Note: This method works correctly only for block logs with a length of at least 30 blocks.
        """
        block_files = self.__block_files_force()
        artifacts_list = self.artifact_files
        if not artifacts_list:
            self.generate_artifacts()
        block_log_arg = ["--block-log", str(block_files[-1])]
        return int(self.__run_and_get_output("--get-head-block-number", *block_log_arg))

    def get_block(self, block_number: int) -> BlockLogUtilResultTransaction | BlockLogUtilResultTransactionLegacy:
        """
        Returns a block from block_log.

        :param block_number: Number of block to return

        Note: This method works correctly only for block logs with a length of at least 30 blocks.
        """
        artifacts_list = self.artifact_files
        if not artifacts_list:
            self.generate_artifacts()
        expected_str: Final[str] = "block_id"

        block_files = self.__block_files_force()
        block_number_arg = ["--block-number", f"{block_number}"]
        output: str = ""
        for log in block_files:
            block_log_arg = ["--block-log", str(log)]
            with contextlib.suppress(BlockLogUtilError):
                output = self.__run_and_get_output("--get-block", *block_log_arg, *block_number_arg).replace("'", '"')
            if expected_str in output:
                try:
                    return BlockLogUtilResultTransaction.parse_builtins(json.loads(output))
                except msgspec.ValidationError:
                    return BlockLogUtilResultTransactionLegacy.parse_builtins(json.loads(output))
        raise BlockLogUtilError(f"Block {block_number} not found or response malformed: `{output}`")

    def get_block_ids(self, block_number: int) -> str:
        """
        Returns a block_ID from block_log.

        :param block_number: ID of block to return

        Note: This method works correctly only for block logs with a length of at least 30 blocks.
        """
        expected_str: Final[str] = "block_id: "

        artifacts_list = self.artifact_files
        if not artifacts_list:
            self.generate_artifacts()

        output = ""
        block_files = self.__block_files_force()
        for file in block_files:
            with contextlib.suppress(BlockLogUtilError):
                output = self.__run_and_get_output(
                    "--get-block-ids", "-n", f"{block_number}", "--block-log", str(file)
                ).replace("'", '"')
            if expected_str in output:
                return output[len(expected_str) :]

        raise BlockLogUtilError(f"Block not found or response malformed: `{output}`")

    @overload
    def get_head_block_time(
        self, serialize: Literal[True], serialize_format: TimeFormats | str = TimeFormats.DEFAULT_FORMAT
    ) -> str:
        ...

    @overload
    def get_head_block_time(
        self, serialize: Literal[False] = False, serialize_format: TimeFormats | str = TimeFormats.DEFAULT_FORMAT
    ) -> datetime:
        ...

    def get_head_block_time(
        self, serialize: bool = False, serialize_format: TimeFormats | str = TimeFormats.DEFAULT_FORMAT
    ) -> str | datetime:
        """
        Get timestamp of head block in block_log.

        :param serialize: Allows choosing whether the time is additionally returned serialized.
        :param serialize_format: Format of serialization.

        Note: This method works correctly only for block logs with a length of at least 30 blocks.
        """
        head_block_num = self.get_head_block_number()
        head_block_timestamp = self.get_block(head_block_num).timestamp
        if serialize:
            return Time.serialize(head_block_timestamp, format_=serialize_format)
        return head_block_timestamp

    @staticmethod
    def __raise_missing_artifacts_error(block_log_artifacts_path: Path) -> None:
        raise MissingBlockLogArtifactsError(
            f"Block log artifacts with following path are missing:\n{block_log_artifacts_path}"
        )
