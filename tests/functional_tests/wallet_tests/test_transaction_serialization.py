import pytest

import test_tools as tt


@pytest.mark.parametrize("transaction_serialization", ["legacy", "hf26"])
def test_transaction_serialization_getter(transaction_serialization):
    wallet = tt.Wallet(additional_arguments=[f"--transaction-serialization={transaction_serialization}"])
    assert wallet.transaction_serialization == transaction_serialization


def test_default_serialization():
    init_node = tt.InitNode()
    init_node.run()

    wallet = tt.Wallet(attach_to=init_node)

    assert wallet.transaction_serialization == "legacy"

    # Check if example transaction really is legacy
    transaction = wallet.api.transfer("initminer", "alice", tt.Asset.Test(3), "memo", broadcast=False)
    assert isinstance(transaction["operations"][0], list)
    assert transaction["operations"][0][1]["amount"] == str(tt.Asset.Test(3))
