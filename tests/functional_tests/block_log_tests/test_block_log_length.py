from pathlib import Path
from typing import Final

import test_tools as tt

BLOCK_LOG_DIRECTORY: Final[Path] = Path(__file__).parent / "block_log"


def test_getting_block_log_length():
    # ARRANGE
    with open(BLOCK_LOG_DIRECTORY / "length", encoding="utf-8") as file:
        expected_length = int(file.read())

    block_log = tt.BlockLog(BLOCK_LOG_DIRECTORY / "block_log")

    # ACT
    actual_length = block_log.length

    # ASSERT
    assert actual_length == expected_length
