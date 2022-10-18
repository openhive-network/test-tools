from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
from typing import Literal, NoReturn, Optional

from test_tools.__private import paths_to_executables
from test_tools.__private.exceptions import MissingBlockLogArtifactsError


class BlockLog:
    def __init__(self, owner, path, *, artifacts: Literal["required", "optional", "excluded"]):
        self.__owner = owner
        self.__path = Path(path)
        self.__artifacts = artifacts

    def __repr__(self):
        return f"<BlockLog: path={self.__path}>"

    @property
    def path(self) -> Path:
        return self.__path

    @property
    def artifacts_path(self) -> Path:
        return self.path.with_suffix(".artifacts")

    def copy_to(
        self, destination, *, artifacts: Optional[Literal["required", "optional", "excluded"]] = None
    ) -> BlockLog:
        """
        Copies block log and its artifacts (if requested via `artifacts` parameter) to specified `destination`. By
        default, only block log is copied and artifacts are excluded.

        It is unsafe to copy block log or use it for replay when node, which is source if block log, is run. It might
        lead to problems, because files referenced by block log object might be modified at the same time by its owner.

        :param destination: Path to directory, where block log (and optionally artifacts) will be copied.
        :param artifacts: Decides how artifacts are handled during block log copying. Allowed values:
            - "required" -- Artifacts are always copied. Missing artifacts are treated as error.
            - "optional" -- Artifacts are copied if exists. This is not a problem when artifacts are missing.
            - "excluded" -- Artifacts are never copied.
        :return: Copy of source block log.
        """
        assert self.__path.exists()

        artifacts = artifacts if artifacts is not None else self.__artifacts

        if artifacts != "excluded":
            if self.artifacts_path.exists():
                shutil.copy(self.artifacts_path, destination)
            elif artifacts == "required":
                self.__raise_missing_artifacts_error(self.artifacts_path)
            else:
                assert artifacts == "optional"

        copied_block_log_path = shutil.copy(self.__path, destination)
        return BlockLog(self.__owner, copied_block_log_path, artifacts=artifacts)

    def truncate(self, output_block_log_path: str, block_number: int):
        subprocess.run(
            [
                paths_to_executables.get_path_of("compress_block_log"),
                f"--input-block-log={self.__path.parent.absolute()}",
                f"--output-block-log={Path(output_block_log_path).parent.absolute()}",
                f"--block-count={block_number}",
                "--decompress",
            ],
            check=True,
        )
        return BlockLog(None, output_block_log_path, artifacts="optional")

    @staticmethod
    def __raise_missing_artifacts_error(block_log_artifacts_path) -> NoReturn:
        raise MissingBlockLogArtifactsError(
            f"Block log artifacts with following path are missing:\n{block_log_artifacts_path}"
        )
