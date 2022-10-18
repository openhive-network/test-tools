from pathlib import Path
from typing import Literal

import pytest

import test_tools as tt


@pytest.fixture
def destination_directory(tmp_path: Path) -> Path:
    """Block log files in tests are copied to this directory."""
    directory = tmp_path / "destination"
    directory.mkdir()
    return directory


@pytest.fixture
def source_directory(tmp_path: Path) -> Path:
    """Block log files in tests are created here and copied from this directory."""
    directory = tmp_path / "source"
    directory.mkdir()
    return directory


@pytest.fixture
def block_log_stub(source_directory) -> Path:
    block_log_stub_path = source_directory / "block_log"
    block_log_stub_path.touch()
    return block_log_stub_path


@pytest.fixture
def artifacts_stub(source_directory) -> Path:
    artifacts_stub_path = source_directory / "block_log.artifacts"
    artifacts_stub_path.touch()
    return artifacts_stub_path


def test_paths_in_copied_block_log(
    block_log_stub, artifacts_stub, destination_directory
):  # pylint: disable=unused-argument
    copied_block_log = __prepare_copy(block_log_stub, destination_directory, artifacts="required")

    assert copied_block_log.path == destination_directory / "block_log"
    assert copied_block_log.artifacts_path == destination_directory / "block_log.artifacts"


def test_copying_when_required_artifacts_exists(
    block_log_stub, artifacts_stub, destination_directory
):  # pylint: disable=unused-argument
    copied_block_log = __prepare_copy(block_log_stub, destination_directory, artifacts="required")
    __assert_files_were_copied(copied_block_log, require_artifacts=True)


def test_copying_when_required_artifacts_are_missing(block_log_stub, destination_directory):
    with pytest.raises(tt.exceptions.MissingBlockLogArtifactsError):
        __prepare_copy(block_log_stub, destination_directory, artifacts="required")

    assert __is_empty(destination_directory)  # When error occurs nothing should be copied.


def test_copying_when_optional_artifacts_exists(
    block_log_stub, artifacts_stub, destination_directory
):  # pylint: disable=unused-argument
    copied_block_log = __prepare_copy(block_log_stub, destination_directory, artifacts="optional")
    __assert_files_were_copied(copied_block_log, require_artifacts=True)


def test_copying_when_optional_artifacts_are_missing(block_log_stub, destination_directory):
    copied_block_log = __prepare_copy(block_log_stub, destination_directory, artifacts="optional")
    __assert_files_were_copied(copied_block_log, require_artifacts=False)


def test_copying_when_excluded_artifacts_exists(
    block_log_stub, artifacts_stub, destination_directory
):  # pylint: disable=unused-argument
    copied_block_log = __prepare_copy(block_log_stub, destination_directory, artifacts="excluded")
    __assert_files_were_copied(copied_block_log, require_artifacts=False)


def test_copying_when_excluded_artifacts_are_missing(block_log_stub, destination_directory):
    copied_block_log = __prepare_copy(block_log_stub, destination_directory, artifacts="excluded")
    __assert_files_were_copied(copied_block_log, require_artifacts=False)


def __is_empty(directory: Path) -> bool:
    assert directory.is_dir()
    return not any(directory.iterdir())


def __prepare_copy(
    source: Path, destination_directory: Path, *, artifacts: Literal["required", "optional", "excluded"]
) -> tt.BlockLog:
    source_block_log = tt.BlockLog(None, source)
    return source_block_log.copy_to(destination_directory, artifacts=artifacts)


def __assert_files_were_copied(
    block_log: tt.BlockLog, *, require_artifacts: bool, require_block_log: bool = True
) -> None:
    # Make sure, that exactly required number of files are copied and nothing more.
    assert len(list(block_log.path.parent.iterdir())) == [require_block_log, require_artifacts].count(True)

    if require_block_log:
        assert block_log.path.exists()

    if require_artifacts:
        assert block_log.artifacts_path.exists()
