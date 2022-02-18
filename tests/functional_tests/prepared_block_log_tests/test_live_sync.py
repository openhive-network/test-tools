# pylint: disable=all
# Check git blame for details
from test_tools.private.prepared_block_log.block_log_utils import all_witness_names


def test_node_replay(world):
    api_node = world.create_api_node()
    world.run_all_nodes(prepared_block_log=True, wait_for_live=False)

    head = api_node.api.database.get_dynamic_global_properties()["head_block_number"]

    assert head == 105


def test_producing_blocks(world):
    witness_node = world.create_witness_node(witnesses=all_witness_names)
    world.run_all_nodes(prepared_block_log=True)

    witness_node.wait_for_block_with_number(106)
