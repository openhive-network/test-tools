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
