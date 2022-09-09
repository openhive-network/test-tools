from typing import Final, Protocol

import pytest

import test_tools as tt


class WalletMaker(Protocol):
    def __call__(self, protocol: str = "http") -> tt.Wallet:
        """Creates wallet fixture attached to node with a given protocol."""


@pytest.fixture
def wallet(request) -> WalletMaker:
    def _wallet(protocol: str = "http") -> tt.Wallet:
        init_node = tt.InitNode()

        shared_file_size = request.node.get_closest_marker("node_shared_file_size")
        if shared_file_size:
            init_node.config.shared_file_size = shared_file_size.args[0]

        init_node.run()

        return tt.Wallet(attach_to=init_node, protocol=protocol)

    return _wallet


@pytest.mark.parametrize("protocol", ["http", "ws"])
def test_keys_import_during_account_creation(protocol: str, wallet: WalletMaker):
    # ARRANGE
    wallet = wallet(protocol=protocol)

    # ACT
    accounts = wallet.create_accounts(3)
    imported_private_keys = set(key_pair[1] for key_pair in wallet.api.list_keys())

    # ASSERT
    assert all(account.private_key in imported_private_keys for account in accounts)


@pytest.mark.node_shared_file_size("16G")
@pytest.mark.parametrize("protocol", ["http", "ws"])
def test_creation_of_huge_number_of_accounts(protocol: str, wallet: WalletMaker):
    # ARRANGE
    wallet = wallet(protocol=protocol)
    number_of_accounts: Final[int] = 200_000

    # ACT
    accounts_before = set(wallet.list_accounts())
    created_accounts = wallet.create_accounts(number_of_accounts, import_keys=False)
    accounts_after = set(wallet.list_accounts())

    # ASSERT
    assert len(created_accounts) == number_of_accounts
    assert len(accounts_after.difference(accounts_before)) == number_of_accounts
