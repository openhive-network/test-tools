import filecmp
from glob import glob as get_files_matching_pattern
import json
from pathlib import Path
import shutil
from typing import Optional


class Snapshot:
    def __init__(self, snapshot_path: Path, block_log_path: Path, block_log_index_path: Path, node=None):
        self.__snapshot_path: Path = snapshot_path
        self.__block_log_path: Path = block_log_path
        self.__block_log_index_path: Optional[Path] = block_log_index_path if block_log_index_path.exists() else None
        self.__creator = node

        if node is not None:
            snapshot_state_path = node.directory / 'state_snapshot_dump.json'
            if not snapshot_state_path.exists():
                self.state = None
                return

            with open(snapshot_state_path, encoding='utf-8') as state_file:
                self.state = json.load(state_file)

    def copy_to(self, node_directory: Path):
        blocklog_directory = node_directory / 'blockchain'
        blocklog_directory.mkdir(exist_ok=True)

        if self.__block_log_path.parent != blocklog_directory:
            shutil.copy(self.__block_log_path, blocklog_directory)

        if self.__block_log_index_path is not None and self.__block_log_index_path.parent != blocklog_directory:
            shutil.copy(self.__block_log_index_path, blocklog_directory)

        destination_snapshot_path = node_directory / 'snapshot'
        if self.__snapshot_path != destination_snapshot_path:
            shutil.copytree(self.__snapshot_path, destination_snapshot_path)

    def get_path(self) -> Path:
        return self.__snapshot_path

    def __repr__(self):
        optional_creator_info = '' if self.__creator is None else f' from {self.__creator}'
        return f'<Snapshot{optional_creator_info}: path={self.__snapshot_path}>'

    def __eq__(self, other) -> bool:
        my_files = sorted(get_files_matching_pattern(f'{self.get_path()}/**/*.sst', recursive=True))
        others_files = sorted(get_files_matching_pattern(f'{other.get_path()}/**/*.sst', recursive=True))

        if len(my_files) != len(others_files):
            return False

        for mine, others in zip(my_files, others_files):
            files_are_same = filecmp.cmp(mine, others, shallow=False)
            if not files_are_same:
                return False

        return True
