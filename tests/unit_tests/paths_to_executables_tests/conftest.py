from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

import pytest
from test_tools.__private.paths_to_executables import _PathsToExecutables

from .executable_init_params import ExecutableInitParams

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture()
def paths() -> _PathsToExecutables:
    """
    Returns PathsToExecutables object without any value from current environment.

    Doesn't matter if user has e.g. set environment variable searched by this object or
    script is run with some command line argument. All such information are ignored.
    """
    paths = _PathsToExecutables()
    paths.parse_command_line_arguments([])
    paths.set_environment_variables({})
    paths.set_installed_executables({})
    return paths


def __executables() -> list[ExecutableInitParams]:
    return [
        ExecutableInitParams("hived", "--hived-path", "HIVED_PATH", "programs/hived/hived"),
        ExecutableInitParams("cli_wallet", "--cli-wallet-path", "CLI_WALLET_PATH", "programs/cli_wallet/cli_wallet"),
        ExecutableInitParams("get_dev_key", "--get-dev-key-path", "GET_DEV_KEY_PATH", "programs/util/get_dev_key"),
        ExecutableInitParams(
            "compress_block_log",
            "--compress-block-log-path",
            "COMPRESS_BLOCK_LOG_PATH",
            "programs/util/compress_block_log",
        ),
        ExecutableInitParams(
            "block_log_util",
            "--block-log-util-path",
            "BLOCK_LOG_UTIL_PATH",
            "programs/util/block_log_util",
        ),
    ]


@pytest.fixture()
def executables() -> list[ExecutableInitParams]:
    return __executables()


@pytest.fixture()
def executable() -> ExecutableInitParams:
    return __executables()[0]


@pytest.fixture()
def prepare_build_like_dir() -> Iterator[Path]:
    with TemporaryDirectory() as temp_path:
        path = Path(temp_path)
        (hived_path := path / "programs" / "hived").mkdir(parents=True)
        (hived_path / "hived").touch()
        (cli_path := path / "programs" / "cli_wallet").mkdir()
        (cli_path / "cli_wallet").touch()
        (util_path := path / "programs" / "util").mkdir()
        (util_path / "get_dev_key").touch()
        (util_path / "compress_block_log").touch()
        (util_path / "block_log_util").touch()

        yield path
