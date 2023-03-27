import pytest

import test_tools as tt


@pytest.mark.requires_haf_executables
def test_p2p_sync():
    network = tt.Network()
    init_node = tt.InitNode(network=network)
    haf_node = tt.HafNode(network=network)
    network.run()

    wallet = tt.Wallet(attach_to=init_node)

    transaction = wallet.api.create_account("initminer", "alice", "{}")

    haf_node.wait_for_transaction_in_database(transaction)
