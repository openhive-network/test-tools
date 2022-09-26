import pytest

import test_tools as tt


@pytest.fixture
def wallet():
    init_node = tt.InitNode()
    init_node.run()

    return tt.Wallet(attach_to=init_node)


def test_if_raise_when_parameters_are_bad(wallet):
    with pytest.raises(tt.exceptions.CommunicationError):
        wallet.api.create_account("surely", "bad", "arguments")


def test_if_raise_when_operation_is_invalid(wallet):
    with pytest.raises(tt.exceptions.CommunicationError):
        # Operation is invalid because account "alice" doesn't exists
        wallet.api.transfer("initminer", "alice", tt.Asset.Test(1), "memo")
