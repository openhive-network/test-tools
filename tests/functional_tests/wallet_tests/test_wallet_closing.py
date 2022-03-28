import test_tools as tt


def test_closing():
    init_node = tt.InitNode()
    init_node.run()

    wallet = tt.Wallet(attach_to=init_node)
    wallet.close()

    assert not wallet.is_running()
