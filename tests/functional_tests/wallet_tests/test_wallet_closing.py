import test_tools as tt


def test_closing(node: tt.InitNode):
    wallet = tt.Wallet(attach_to=node)
    wallet.close()

    assert not wallet.is_running()
