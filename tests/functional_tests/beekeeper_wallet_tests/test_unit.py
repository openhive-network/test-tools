from __future__ import annotations

import test_tools as tt
from test_tools.__private.account import Account

import pytest

@pytest.fixture
def node() -> tt.InitNode:
    node = tt.InitNode()
    node.run()
    return node

@pytest.fixture
def wallet(node: tt.InitNode) -> tt.BeekeeperWallet:
    wallet = tt.BeekeeperWallet(attach_to=node)
    return wallet

def test_in_single_transaction(wallet: tt.BeekeeperWallet) -> None:
    wallet.api.create_account("initminer", "alice", "{}")
    with wallet.in_single_transaction() as trx:
        wallet.api.post_comment(
            "initminer", "test-permlink", "", "test-parent-permlink", "test-title", "test-body", "{}"
        )
        wallet.api.post_comment(
            "alice", "test-permlink1", "", "test-parent-permlink1", "test-title1", "test-body1", "{}"
        )

def test_create_account(wallet: tt.BeekeeperWallet) -> None:
    wallet.api.create_account("initminer", "alice", "{}")

def test_post_comment(wallet: tt.BeekeeperWallet) -> None:
    wallet.api.create_account("initminer", "alice", "{}")
    wallet.api.post_comment(
        "initminer", "test-permlink", "", "test-parent-permlink", "test-title", "test-body", "{}"
    )

def test_create_account_with_keys(wallet: tt.BeekeeperWallet) -> None:
    alice = tt.Account('alice')
    wallet.api.create_account_with_keys(
        "initminer", alice.name, "{}", alice.public_key, alice.public_key, alice.public_key, alice.public_key, broadcast=False
    )

def test_create_account_with_keys(wallet: tt.BeekeeperWallet) -> None:
    alice = tt.Account('alice')
    wallet.api.create_account_with_keys(
        "initminer", alice.name, "{}", alice.public_key, alice.public_key, alice.public_key, alice.public_key, broadcast=False
    )

# def test_create_account_delegated(wallet: tt.BeekeeperWallet) -> None:
#     # try:
#     wallet.api.create_account_delegated("initminer", tt.Asset.Test(3), tt.Asset.Test(6.123456), "alicex", "{}")
#     # except Exception as e:
#     #     message = str(e)
#     #     found = message.find("Account creation with delegation is deprecated as of Hardfork 20")
#     #     assert found != -1

# def test_create_account_delegated_with_keys(wallet: tt.BeekeeperWallet) -> None:
#     # try:
#     wallet.api.create_account_delegated("initminer", tt.Asset.Test(3), tt.Asset.Test(6.123456), "alicex", "{}")
#     # except Exception as e:
#     #     message = str(e)
#     #     found = message.find("Account creation with delegation is deprecated as of Hardfork 20")
#     #     assert found != -1

def test_create_order(wallet: tt.BeekeeperWallet) -> None:
    wallet.create_account("alice", hives=tt.Asset.Test(100), vests=tt.Asset.Test(100))
    wallet.api.create_order("initminer", 1000, tt.Asset.Test(100), tt.Asset.Tbd(100), False, 1000)
    # problem z authority

def test_transfer(wallet: tt.BeekeeperWallet) -> None:
    wallet.api.create_account("initminer", "alice", "{}")
    wallet.api.transfer("initminer", "alice", tt.Asset.Test(500), "banana")

def test_transfer_to_vesting(wallet: tt.BeekeeperWallet) -> None:
    wallet.api.create_account("initminer", "alice", "{}")
    wallet.api.transfer_to_vesting("initminer", "alice", tt.Asset.Hive(500))

