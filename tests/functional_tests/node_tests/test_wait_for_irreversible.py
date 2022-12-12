import pytest

import test_tools as tt


def test_raising_timeout():
    # ARRANGE
    node = tt.InitNode()
    node.run()

    # ACT & ASSERT
    with pytest.raises(TimeoutError):
        node.wait_for_irreversible_block(100, timeout=0.1)


@pytest.mark.parametrize("include_number_param", [False, True], ids=("current_head_block", "block_with_number"))
def test_waiting_for_irreversible_block(include_number_param: bool):
    # ARRANGE
    node = tt.InitNode()
    node.run()
    last_block_number = node.get_last_block_number()

    # ACT
    node.wait_for_irreversible_block(number=last_block_number if include_number_param else None)

    # ASSERT
    assert node.get_last_irreversible_block_number() >= last_block_number
