import test_tools as tt


def test_if_snapshot_is_dumped_and_node_continues_to_run():
    init_node = tt.InitNode()
    init_node.run()

    init_node.dump_snapshot()
    assert init_node.is_running()


def test_if_snapshot_is_dumped_and_node_is_closed():
    init_node = tt.InitNode()
    init_node.run()

    init_node.dump_snapshot(close=True)
    assert not init_node.is_running()


def test_if_operation_could_be_created_right_after_dumping_snapshot():
    # ARRANGE
    init_node = tt.InitNode()
    init_node.run()
    wallet = tt.Wallet(attach_to=init_node)

    # ACT
    wallet.create_account("alice")

    # wait for the block with the transaction to become irreversible, and will be saved in block_log
    init_node.wait_number_of_blocks(21)

    wallet.close()
    init_node.dump_snapshot()
    wallet.run()

    wallet.create_account("bob")

    # ASSERT
    assert init_node.api.wallet_bridge.list_accounts("", 2) == ["alice", "bob"]
