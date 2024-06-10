from __future__ import annotations

import pytest
import test_tools as tt

# hasz22


@pytest.fixture()
def wallet(request: pytest.FixtureRequest) -> tt.Wallet:
    init_node = tt.InitNode()

    shared_file_size = request.node.get_closest_marker("node_shared_file_size")
    if shared_file_size:
        init_node.config.shared_file_size = shared_file_size.args[0]

    init_node.run()

    return tt.Wallet(attach_to=init_node)


def test_keys_import_during_account_creation(wallet: tt.Wallet) -> None:
    accounts = wallet.create_accounts(3)
    imported_private_keys = wallet.api.list_keys()

    assert all(account.public_key in imported_private_keys for account in accounts)


@pytest.mark.node_shared_file_size("16G")
def test_creation_of_huge_number_of_accounts(wallet: tt.Wallet) -> None:
    amount_of_accounts_to_create = 200_000

    accounts_before = set(wallet.list_accounts())
    created_accounts = wallet.create_accounts(amount_of_accounts_to_create, import_keys=False)
    accounts_after = set(wallet.list_accounts())

    assert len(created_accounts) == amount_of_accounts_to_create
    assert len(accounts_after.difference(accounts_before)) == amount_of_accounts_to_create
