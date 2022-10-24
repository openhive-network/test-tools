import pytest

import test_tools as tt


def test_init_node_startup():
    init_node = tt.InitNode()
    init_node.run()
    init_node.wait_for_block_with_number(1)


def test_startup_timeout():
    node = tt.WitnessNode(witnesses=[])
    with pytest.raises(TimeoutError):
        node.run(timeout=2)


def test_loading_own_snapshot():
    init_node = tt.InitNode()
    init_node.run()

    make_transaction_for_test(init_node)
    generate_blocks(init_node, 100)  # To make sure, that block with test operation will be stored in block log
    snapshot = init_node.dump_snapshot(close=True)

    # Node is not waiting for live here, because of blocks generation behavior.
    # After N blocks generation, node will stop blocks production for N * 3s.
    init_node.run(load_snapshot_from=snapshot, wait_for_live=False)
    assert_that_transaction_for_test_has_effect(init_node)


def test_loading_snapshot_from_other_node():
    init_node = tt.InitNode()
    init_node.run()

    make_transaction_for_test(init_node)
    generate_blocks(init_node, 100)  # To make sure, that block with test operation will be stored in block log
    snapshot = init_node.dump_snapshot()

    loading_node = tt.ApiNode()
    loading_node.run(load_snapshot_from=snapshot, wait_for_live=False)
    assert_that_transaction_for_test_has_effect(loading_node)


def test_loading_snapshot_from_custom_path():
    init_node = tt.InitNode()
    init_node.run()

    make_transaction_for_test(init_node)
    generate_blocks(init_node, 100)  # To make sure, that block with test operation will be stored in block log
    snapshot = init_node.dump_snapshot()

    loading_node = tt.ApiNode()
    loading_node.run(load_snapshot_from=snapshot.get_path(), wait_for_live=False)
    assert_that_transaction_for_test_has_effect(loading_node)


def test_replay_from_other_node_block_log():
    init_node = tt.InitNode()
    init_node.run()

    make_transaction_for_test(init_node)
    generate_blocks(init_node, 100)  # To make sure, that block with test operation will be stored in block log
    init_node.close()

    replaying_node = tt.ApiNode()
    replaying_node.run(replay_from=init_node.block_log, wait_for_live=False)
    assert_that_transaction_for_test_has_effect(replaying_node)


def test_replay_until_specified_block():
    init_node = tt.InitNode()
    init_node.run()
    generate_blocks(init_node, 100)
    init_node.close()

    replaying_node = tt.ApiNode()
    replaying_node.run(replay_from=init_node.block_log, stop_at_block=50, wait_for_live=False)
    assert replaying_node.get_last_block_number() == 50


def test_replay_from_external_block_log():
    init_node = tt.InitNode()
    init_node.run()
    generate_blocks(init_node, 100)
    init_node.close()

    # Rename block log, to check if block logs with changed names are also handled.
    external_block_log = init_node.block_log.copy_to(tt.context.get_current_directory() / "external_block_log")

    replaying_node = tt.ApiNode()
    replaying_node.run(replay_from=external_block_log.path, stop_at_block=50, wait_for_live=False)
    assert replaying_node.get_last_block_number() == 50


def test_exit_before_synchronization():
    init_node = tt.InitNode()
    init_node.run(exit_before_synchronization=True)
    assert not init_node.is_running()


def test_restart():
    init_node = tt.InitNode()
    init_node.run()
    init_node.restart()


def test_startup_with_modified_time():
    requested_start_time = tt.Time.parse("2020-01-01T00:00:00")

    init_node = tt.InitNode()
    init_node.run(time_offset=f'{tt.Time.serialize(requested_start_time, format_="@%Y-%m-%d %H:%M:%S")}')

    node_time = tt.Time.parse(init_node.api.database.get_dynamic_global_properties()["time"])

    # Some time may pass between node start and getting time, so below comparison is made with a few block tolerance.
    assert tt.Time.are_close(requested_start_time, node_time, absolute_tolerance=tt.Time.seconds(15))


def make_transaction_for_test(node):
    wallet = tt.Wallet(attach_to=node)
    wallet.api.create_account("initminer", "alice", "{}")


def assert_that_transaction_for_test_has_effect(node):
    response = node.api.database.find_accounts(accounts=["alice"], delayed_votes_active=False)
    assert response["accounts"][0]["name"] == "alice"


def generate_blocks(node, number_of_blocks):
    tt.logger.info(f"Generation of {number_of_blocks} blocks started...")
    node.api.debug_node.debug_generate_blocks(
        debug_key=tt.Account("initminer").private_key,
        count=number_of_blocks,
        skip=0,
        miss_blocks=0,
        edit_if_needed=True,
    )
    tt.logger.info("Blocks generation finished.")
