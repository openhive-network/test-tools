from pathlib import Path
from typing import Final

import test_tools as tt

BLOCK_LOG_LENGTH: Final[int] = 30
BLOCK_LOG_DIRECTORY: Final[Path] = Path(__file__).parent


def main():
    node = tt.InitNode()
    node.run()
    node.wait_for_block_with_number(BLOCK_LOG_LENGTH)

    head_block_num = node.get_last_block_number()
    head_block_timestamp = node.api.block.get_block(block_num=head_block_num)['block']['timestamp']

    node.close()

    node.block_log.copy_to(BLOCK_LOG_DIRECTORY)

    with open(BLOCK_LOG_DIRECTORY / "length", "w", encoding="utf-8") as file:
        file.write(str(head_block_num))

    with open(BLOCK_LOG_DIRECTORY / "timestamp", "w", encoding="utf-8") as file:
        file.write(head_block_timestamp)


if __name__ == "__main__":
    main()
