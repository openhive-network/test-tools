from __future__ import annotations

import test_tools as tt
from test_tools.__private.account import Account

from helpy.exceptions import RequestError

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

def test_create_account_delegated(wallet: tt.BeekeeperWallet) -> None:
    try:
        wallet.api.create_account_delegated("initminer", tt.Asset.Test(3), tt.Asset.Vest(6.123456), "alicex", "{}")
    except (RequestError) as e:
        message = str(e)
        found = message.find("Account creation with delegation is deprecated as of Hardfork 20")
        assert found != -1

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

# def test_cancel_order(wallet: tt.BeekeeperWallet) -> None:
#     wallet.create_account("alice", hives=tt.Asset.Test(100), vests=tt.Asset.Test(100))
#     wallet.api.create_order("initminer", 1000, tt.Asset.Test(100), tt.Asset.Tbd(100), False, 1000)
#     wallet.api.cancel_order("initminer", 0)
#     # problem z authority, unknown key

def test_transfer(wallet: tt.BeekeeperWallet) -> None:
    wallet.api.create_account("initminer", "alice", "{}")
    wallet.api.transfer("initminer", "alice", tt.Asset.Test(500), "banana")

def test_transfer_to_vesting(wallet: tt.BeekeeperWallet) -> None:
    wallet.api.create_account("initminer", "alice", "{}")
    wallet.api.transfer_to_vesting("initminer", "alice", tt.Asset.Hive(500))

def test_create_proposal(wallet: tt.BeekeeperWallet) -> None:
    # problem z authority
    wallet.create_account("alice", hbds=tt.Asset.Tbd(1000000), vests=tt.Asset.Test(1000000))
    wallet.api.post_comment("initminer", "permlink", "", "parent-permlink", "title", "body", "{}")
    wallet.api.create_proposal(
        "initminer",
        "initminer",
        tt.Time.from_now(weeks=16),
        tt.Time.from_now(weeks=20),
        tt.Asset.Tbd(1000000),
        "subject-1",
        "permlink",
    )

def test_update_proposal(wallet: tt.BeekeeperWallet) -> None:
    # problem z authority
    wallet.create_account("alice", hbds=tt.Asset.Tbd(1000000), vests=tt.Asset.Test(1000000))
    wallet.api.post_comment("initminer", "permlink", "", "parent-permlink", "title", "body", "{}")
    proposal = wallet.api.create_proposal(
        "initminer",
        "initminer",
        tt.Time.from_now(weeks=16),
        tt.Time.from_now(weeks=20),
        tt.Asset.Tbd(1000000),
        "subject-1",
        "permlink",
    )

    wallet.api.update_proposal(
        0,
        "initminer",
        tt.Asset.Tbd(1000000),
        "subject-1",
        "permlink",
        tt.Time.from_now(weeks=19),
    )

def test_remove_proposal(wallet: tt.BeekeeperWallet) -> None:
    # problem z authority
    wallet.create_account("alice", hbds=tt.Asset.Tbd(1000000), vests=tt.Asset.Test(1000000))
    wallet.api.post_comment("initminer", "permlink", "", "parent-permlink", "title", "body", "{}")
    proposal = wallet.api.create_proposal(
        "initminer",
        "initminer",
        tt.Time.from_now(weeks=16),
        tt.Time.from_now(weeks=20),
        tt.Asset.Tbd(1000000),
        "subject-1",
        "permlink",
    )

    wallet.api.remove_proposal(
        "initminer",
        [0],
    )

def test_update_proposal_votes(wallet: tt.BeekeeperWallet) -> None:
    # problem z authority
    wallet.create_account("alice", hbds=tt.Asset.Tbd(1000000), vests=tt.Asset.Test(1000000))
    wallet.api.post_comment("initminer", "permlink", "", "parent-permlink", "title", "body", "{}")
    wallet.api.create_proposal(
        "initminer",
        "initminer",
        tt.Time.from_now(weeks=16),
        tt.Time.from_now(weeks=20),
        tt.Asset.Tbd(1000000),
        "subject-1",
        "permlink",
    )

    wallet.api.update_proposal_votes("initminer", [0], True)

def test_cancel_transfer_from_savings(wallet: tt.BeekeeperWallet) -> None:
    # Nie ma, za trudne do wytestowania
    pass

def test_change_recovery_account(wallet: tt.BeekeeperWallet) -> None:
    # wallet.create_account("alice", hives=tt.Asset.Test(100), vests=tt.Asset.Test(100))
    wallet.api.change_recovery_account("initminer", "initminer")

def test_claim_reward_balance(wallet: tt.BeekeeperWallet) -> None:
    # Nie ma, za trudne do wytestowania
    pass

def test_convert_hbd(wallet: tt.BeekeeperWallet) -> None:
    wallet.api.convert_hbd("initminer", tt.Asset.Tbd(1.25))

def test_convert_hive_with_collateral(wallet: tt.BeekeeperWallet) -> None:
        wallet.api.convert_hive_with_collateral("initminer", tt.Asset.Test(10))

def test_decline_voting_rights(wallet: tt.BeekeeperWallet) -> None:
    wallet.api.decline_voting_rights("initminer", True)

def test_decrypt_memo(wallet: tt.BeekeeperWallet) -> None:
    wallet.api.decline_voting_rights("initminer", True)

def test_delegate_vesting_shares(wallet: tt.BeekeeperWallet) -> None:
    wallet.api.create_account("initminer", "tipu", "{}")
    wallet.api.delegate_vesting_shares("initminer", "tipu", tt.Asset.Vest(0.005))

def test_delegate_vesting_shares_and_transfer(wallet: tt.BeekeeperWallet) -> None:
    wallet.api.create_account("initminer", "alice", "{}")
    wallet.api.delegate_vesting_shares_and_transfer(
        "initminer", "alice", tt.Asset.Vest(1), tt.Asset.Test(6), "transfer_memo"
    )

# def test_encrow_release(wallet: tt.BeekeeperWallet) -> None:
#     # problem z authority
#     wallet.create_account("alice", vests=tt.Asset.Test(50))
#     wallet.create_account("bob", vests=tt.Asset.Test(50))

#     wallet.api.escrow_transfer(
#         "initminer",
#         "alice",
#         "bob",
#         99,
#         tt.Asset.Tbd(1),
#         tt.Asset.Test(2),
#         tt.Asset.Tbd(1),
#         tt.Time.from_now(weeks=16),
#         tt.Time.from_now(weeks=20),
#         "{}",
#     )

#     wallet.api.escrow_approve("initminer", "alice", "bob", "bob", 99, True)

#     wallet.api.escrow_approve("initminer", "alice", "bob", "alice", 99, True)

#     wallet.api.escrow_dispute("initminer", "alice", "bob", "initminer", 99)

#     wallet.api.escrow_release(
#         "initminer", "alice", "bob", "bob", "alice", 99, tt.Asset.Tbd(1), tt.Asset.Test(2)
#     )

# def test_escrow_dispute(wallet: tt.BeekeeperWallet) -> None:
#     # problem z authority
#     wallet.create_account("alice", vests=tt.Asset.Test(50))
#     wallet.create_account("bob", vests=tt.Asset.Test(50))

#     wallet.api.escrow_transfer(
#         "initminer",
#         "alice",
#         "bob",
#         99,
#         tt.Asset.Tbd(1),
#         tt.Asset.Test(2),
#         tt.Asset.Tbd(1),
#         tt.Time.from_now(weeks=16),
#         tt.Time.from_now(weeks=20),
#         "{}",
#     )

#     wallet.api.escrow_approve("initminer", "alice", "bob", "bob", 99, True)

#     wallet.api.escrow_approve("initminer", "alice", "bob", "alice", 99, True)

#     wallet.api.escrow_dispute("initminer", "alice", "bob", "initminer", 99)

# def test_escrow_approve(wallet: tt.BeekeeperWallet) -> None:
#     # problem z authority
#     wallet.create_account("alice", vests=tt.Asset.Test(50))
#     wallet.create_account("bob", vests=tt.Asset.Test(50))

#     wallet.api.escrow_transfer(
#         "initminer",
#         "alice",
#         "bob",
#         99,
#         tt.Asset.Tbd(1),
#         tt.Asset.Test(2),
#         tt.Asset.Tbd(1),
#         tt.Time.from_now(weeks=16),
#         tt.Time.from_now(weeks=20),
#         "{}",
#     )

#     wallet.api.escrow_approve("initminer", "alice", "bob", "bob", 99, True)

# def test_escrow_transfer(wallet: tt.BeekeeperWallet) -> None:
#     # problem z authority
#     wallet.create_account("alice", vests=tt.Asset.Test(50))
#     wallet.create_account("bob", vests=tt.Asset.Test(50))

#     wallet.api.escrow_transfer(
#         "initminer",
#         "alice",
#         "bob",
#         99,
#         tt.Asset.Tbd(1),
#         tt.Asset.Test(2),
#         tt.Asset.Tbd(1),
#         tt.Time.from_now(weeks=16),
#         tt.Time.from_now(weeks=20),
#         "{}",
#     )

def test_is_locked(wallet: tt.BeekeeperWallet) -> None:
    wallet.api.is_locked()

def test_publish_feed(wallet: tt.BeekeeperWallet) -> None:
    wallet.api.publish_feed("initminer", {"base": "1.167 TBD", "quote": "1.111 TESTS"})
