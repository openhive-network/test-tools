from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
from typing import Literal, NoReturn

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

    def copy_to(self, destination) -> BlockLog:
        assert self.__path.exists()

        if self.__artifacts != "excluded":
            if self.artifacts_path.exists():
                shutil.copy(self.artifacts_path, destination)
            elif self.__artifacts == "required":
                self.__raise_missing_artifacts_error(self.artifacts_path)
            else:
                assert self.__artifacts == "optional"

        copied_block_log_path = shutil.copy(self.__path, destination)
        return BlockLog(self.__owner, copied_block_log_path, artifacts=self.__artifacts)

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
