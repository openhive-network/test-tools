from pathlib import Path
import shutil
import subprocess
import warnings

from test_tools.__private import paths_to_executables


class BlockLog:
    def __init__(self, owner, path, *, include_artifacts=True):
        self.__owner = owner
        self.__path = Path(path)
        self.__include_artifacts = include_artifacts

    def __repr__(self):
        return f"<BlockLog: path={self.__path}>"

    def get_path(self):
        return self.__path

    def copy_to(self, destination):
        shutil.copy(self.__path, destination)

        if self.__include_artifacts:
            block_log_artifacts_file_name = f"{self.__path.name}.artifacts"
            block_log_artifacts_path = self.__path.with_name(block_log_artifacts_file_name)
            if block_log_artifacts_path.exists():
                shutil.copy(block_log_artifacts_path, destination)
            else:
                self.__warn_about_missing_artifacts(block_log_artifacts_path)

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
        return BlockLog(None, output_block_log_path)

    def __warn_about_missing_artifacts(self, block_log_artifacts_path):
        if self.__owner is not None:
            hint_for_excluding_artifacts = "node.get_block_log(include_artifacts=False)"
        else:
            hint_for_excluding_artifacts = (
                f"import test_tools as tt\n"
                f"block_log = tt.BlockLog('{self.__path}', include_artifacts=False)"
            )  # fmt: skip

        warnings.warn(
            f"Block log with following path is missing:\n"
            f"{block_log_artifacts_path}\n"
            f"\n"
            f"If you want to use block log without artifacts, set include_artifacts flag to False like:\n"
            f"{hint_for_excluding_artifacts}"
        )
