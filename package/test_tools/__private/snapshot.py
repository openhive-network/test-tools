from __future__ import annotations

import contextlib
import filecmp
import json
import shutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from test_tools.__private.node import Node


class Snapshot:
    def __init__(
        self, snapshot_path: Path, block_log_path: Path, block_log_artifacts_path: Path, node: Node | None = None
    ) -> None:
        self.__snapshot_path: Path = snapshot_path
        self.__block_log_path: Path = block_log_path
        self.__block_log_artifacts_path: Path | None = (
            block_log_artifacts_path if block_log_artifacts_path.exists() else None
        )
        self.__creator = node

        if node is not None:
            snapshot_state_path = node.directory / "state_snapshot_dump.json"
            if not snapshot_state_path.exists():
                self.state = None
                return

            with snapshot_state_path.open(encoding="utf-8") as state_file:
                self.state = json.load(state_file)

    def copy_to(self, node_directory: Path) -> None:
        block_log_directory = node_directory / "blockchain"
        block_log_directory.mkdir(exist_ok=True)

        self.__copy_file(self.__block_log_path, block_log_directory)
        self.__copy_file(self.__block_log_artifacts_path, block_log_directory, allow_missing=True)

        destination_snapshot_path = node_directory / "snapshot"
        if self.__snapshot_path != destination_snapshot_path:
            shutil.copytree(self.__snapshot_path, destination_snapshot_path)

    @staticmethod
    def __copy_file(source: Path | None, destination: Path, *, allow_missing: bool = False) -> None:
        if allow_missing and source is None or source is None:
            return

        with contextlib.suppress(
            shutil.SameFileError
        ):  # It's ok, just skip copying because user want to load node's own snapshot.
            shutil.copy(source, destination)

    def get_path(self) -> Path:
        return self.__snapshot_path

    def __repr__(self) -> str:
        optional_creator_info = "" if self.__creator is None else f" from {self.__creator}"
        return f"<Snapshot{optional_creator_info}: path={self.__snapshot_path}>"

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, Snapshot)

        my_files = sorted(self.get_path().rglob("*.sst"))
        others_files = sorted(other.get_path().rglob("*.sst"))

        if len(my_files) != len(others_files):
            return False

        for mine, others in zip(my_files, others_files, strict=False):
            files_are_same = filecmp.cmp(mine, others, shallow=False)
            if not files_are_same:
                return False

        return True
