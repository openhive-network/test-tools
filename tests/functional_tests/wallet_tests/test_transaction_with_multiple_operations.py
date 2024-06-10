from __future__ import annotations

import pytest
import test_tools as tt

from helpy import Hf26Asset as Asset


@pytest.fixture()
def wallet(node: tt.InitNode) -> tt.OldWallet:
    return tt.OldWallet(attach_to=node)


def test_sending_transaction_with_multiple_operations(wallet: tt.OldWallet) -> None:
    accounts_and_balances = {
        "first": Asset.Test(100).as_legacy(),
        "second": Asset.Test(200).as_legacy(),
        "third": Asset.Test(300).as_legacy(),
    }

    with wallet.in_single_transaction():
        for account, amount in accounts_and_balances.items():
            wallet.api.create_account("initminer", account, "{}")
            wallet.api.transfer("initminer", account, amount, "memo")

    for account, expected_balance in accounts_and_balances.items():
        balance = wallet.api.get_account(account)["balance"]
        assert balance == expected_balance


def test_sending_transaction_with_multiple_operations_without_broadcast(wallet: tt.OldWallet) -> None:
    with wallet.in_single_transaction(broadcast=False) as transaction:
        wallet.api.create_account("initminer", "alice", "{}")

    # Generated transaction can be accessed
    assert transaction.get_response() is not None

    # Transaction isn't send
    response = wallet.api.list_accounts("", 100)
    assert "alice" not in response


def test_setting_broadcast_when_building_transaction(wallet: tt.OldWallet) -> None:
    """
    During transaction building every wallet api call shouldn't be broadcasted.

    This test checks if when user do this, appropriate error is generated.
    """
    with wallet.in_single_transaction(), pytest.raises(RuntimeError):
        wallet.api.create_account("initminer", "alice", "{}", True)


def test_getting_response(wallet: tt.OldWallet) -> None:
    with wallet.in_single_transaction() as transaction:
        wallet.api.create_account("initminer", "alice", "{}")
        wallet.api.transfer("initminer", "alice", Asset.Test(100), "memo")

    assert transaction.get_response() is not None
