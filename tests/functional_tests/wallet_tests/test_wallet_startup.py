import pytest
import test_tools as tt


def test_attaching_wallet_to_local_node():
    node = tt.InitNode()
    node.run()

    tt.Wallet(attach_to=node)


def test_attaching_wallet_to_remote_node():
    # Connecting with real remote node (e.g. from main net) is not reliable,
    # so wallet is connected to local node, but via remote node interface.
    local_node = tt.InitNode()
    local_node.run()

    remote_node = tt.RemoteNode(local_node.http_endpoint, ws_endpoint=local_node.ws_endpoint)

    tt.Wallet(attach_to=remote_node)


def test_attaching_wallet_to_not_run_node():
    node = tt.InitNode()

    with pytest.raises(tt.exceptions.NodeIsNotRunning):
        tt.Wallet(attach_to=node)


def test_offline_mode_startup():
    tt.Wallet()


def test_restart():
    node = tt.InitNode()
    node.run()

    wallet = tt.Wallet(attach_to=node)
    wallet.restart()


def __restart_wallet_manually(wallet: tt.Wallet):
    wallet.close()
    wallet.run()


@pytest.mark.parametrize(
    'restart',
    [
        __restart_wallet_manually,
        lambda wallet: wallet.restart,
    ]
)
def test_if_keys_are_stored_after_restart(restart):
    init_node = tt.InitNode()
    init_node.run()

    wallet = tt.Wallet(attach_to=init_node)
    assert len(wallet.api.list_keys()) == 1  # After start only initminer key is registered

    wallet.api.create_account('initminer', 'alice', '')
    assert len(wallet.api.list_keys()) == 5  # After account creation 4 new keys were register

    restart(wallet)

    assert len(wallet.api.list_keys()) == 5  # After restart keys still should be register


def test_if_keys_are_stored_after_together_wallet_and_node_restart():
    init_node = tt.InitNode()
    init_node.run()

    wallet = tt.Wallet(attach_to=init_node)
    assert len(wallet.api.list_keys()) == 1  # After start only initminer key is registered

    wallet.api.create_account('initminer', 'alice', '')
    assert len(wallet.api.list_keys()) == 5  # After account creation 4 new keys were register

    wallet.close()
    init_node.close()

    init_node.run()
    wallet.run()

    assert len(wallet.api.list_keys()) == 5  # After restart keys still should be register
