from __future__ import annotations

import pytest
import test_tools as tt
from test_tools.__private.exceptions import BlockLogUtilError

from schemas.apis.block_api.response_schemas import GetBlockBase


@pytest.fixture()
def node() -> tt.InitNode:
    node = tt.InitNode()
    node.run(time_offset="+0h x10")
    node.wait_for_block_with_number(30)
    time_offset = node.get_head_block_time()
    node.restart(time_offset=tt.Time.serialize(time_offset, format_=tt.TimeFormats.TIME_OFFSET_FORMAT))
    return node


def test_get_head_block_number(node: tt.InitNode) -> None:
    block_log = node.block_log

    head_block_number_from_node = node.get_last_block_number()
    node.close()
    assert (
        block_log.get_head_block_number() == head_block_number_from_node
    ), "Head_block_number from block_log is other than head_block_number from node"


def test_get_block(node: tt.InitNode) -> None:
    block_log = node.block_log

    block_from_node = node.api.block.get_block(block_num=10)
    node.close()

    block_from_block_log = block_log.get_block(block_number=10)
    assert isinstance(block_from_node, GetBlockBase)
    assert (
        block_from_node.block.previous == block_from_block_log.previous
    ), "Get_block from block_log getting other block than get_block from node"


def test_get_head_block_time(node: tt.InitNode) -> None:
    block_log = node.block_log

    head_block_time_from_node = node.get_head_block_time()
    node.close()

    head_block_time_from_block_log = block_log.get_head_block_time()
    head_block_time_from_block_log_serialized = block_log.get_head_block_time(
        serialize=True, serialize_format=tt.TimeFormats.TIME_OFFSET_FORMAT
    )

    assert (
        head_block_time_from_node == head_block_time_from_block_log
    ), "Head_block_time from block_log is other than head_block_time from node"

    assert (
        tt.Time.serialize(time=head_block_time_from_node, format_=tt.TimeFormats.TIME_OFFSET_FORMAT)
        == head_block_time_from_block_log_serialized
    ), "Serialized head_block_time from block_log is other than serialized head_block_time from node"


def test_generate_artifacts(node: tt.InitNode) -> None:
    block_log = node.block_log
    node.close()

    if block_log.artifacts_path.exists():
        block_log.artifacts_path.unlink()

    assert not block_log.artifacts_path.exists()
    block_log.generate_artifacts()
    assert block_log.artifacts_path.exists(), "Block_log.artifacts was not generated"


def test_exception_handling(node: tt.InitNode) -> None:
    block_log = node.block_log
    node.close()
    with pytest.raises(BlockLogUtilError) as error:
        block_log.get_block("incorrect_block_num")  # type: ignore

    assert "the argument ('incorrect_block_num') for option '--block-number' is invalid" in str(
        error.value
    ), "Incorrect error message"


def test_get_block_ids(node: tt.InitNode) -> None:
    block_log = node.block_log

    block_id_from_node = node.api.block.get_block(block_num=10)
    node.close()

    block_id_from_block_log = block_log.get_block_ids(block_number=10)
    assert isinstance(block_id_from_node, GetBlockBase)
    assert (
        block_id_from_node.block.block_id == block_id_from_block_log
    ), "The block_id in node differs from the block_id in block_log."
