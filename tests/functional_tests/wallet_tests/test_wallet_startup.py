import pytest

import test_tools as tt


def test_attaching_wallet_to_local_node(node: tt.InitNode):
    tt.Wallet(attach_to=node)


@pytest.mark.parametrize("with_ws_endpoint", [False, True], ids=("with_http_endpoint", "with_ws_endpoint"))
def test_attaching_wallet_to_remote_node(with_ws_endpoint: bool):
    # Connecting with real remote node (e.g. from main net) is not reliable,
    # so wallet is connected to local node, but via remote node interface.
    local_node = tt.InitNode()
    local_node.run()

    ws_endpoint = {"ws_endpoint": local_node.get_ws_endpoint()} if with_ws_endpoint else {}
    protocol = "ws" if with_ws_endpoint else "http"

    remote_node = tt.RemoteNode(local_node.get_http_endpoint(), **ws_endpoint)

    tt.Wallet(attach_to=remote_node, protocol=protocol)


def test_attaching_wallet_to_remote_node_without_providing_ws_endpoint():
    local_node = tt.InitNode()
    local_node.run()

    remote_node = tt.RemoteNode(local_node.get_http_endpoint())

    with pytest.raises(ValueError):
        tt.Wallet(attach_to=remote_node, protocol="ws")


def test_attaching_wallet_to_not_run_node():
    node = tt.InitNode()

    with pytest.raises(tt.exceptions.NodeIsNotRunning):
        tt.Wallet(attach_to=node)


def test_offline_mode_startup():
    tt.Wallet()


def test_restart(node: tt.InitNode):
    wallet = tt.Wallet(attach_to=node)
    wallet.restart()


def __restart_wallet_manually(wallet: tt.Wallet):
    wallet.close()
    wallet.run()


@pytest.mark.parametrize(
    "restart",
    [
        __restart_wallet_manually,
        lambda wallet: wallet.restart,
    ],
)
def test_if_keys_are_stored_after_restart(restart, node: tt.InitNode):
    wallet = tt.Wallet(attach_to=node)
    assert len(wallet.api.list_keys()) == 1  # After start only initminer key is registered

    wallet.api.create_account("initminer", "alice", "")
    assert len(wallet.api.list_keys()) == 5  # After account creation 4 new keys were register

    restart(wallet)

    assert len(wallet.api.list_keys()) == 5  # After restart keys still should be register


def test_if_keys_are_stored_after_together_wallet_and_node_restart(node: tt.InitNode):
    wallet = tt.Wallet(attach_to=node)
    assert len(wallet.api.list_keys()) == 1  # After start only initminer key is registered

    wallet.api.create_account("initminer", "alice", "")
    assert len(wallet.api.list_keys()) == 5  # After account creation 4 new keys were register

    wallet.close()
    node.close()

    node.run()
    wallet.run()

    assert len(wallet.api.list_keys()) == 5  # After restart keys still should be register
