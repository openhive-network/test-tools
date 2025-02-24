from __future__ import annotations

from typing import TYPE_CHECKING

from test_tools.__private.node import Node
from test_tools.__private.remote_node import RemoteNode
from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.user_handles.handle import Handle
from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase
from test_tools.__private.user_handles.handles.node_handles.remote_node_handle import RemoteNodeHandle
from test_tools.__private.wallet.wallet import Wallet

if TYPE_CHECKING:
    from pathlib import Path

    from schemas.fields.hex import Hex
    from schemas.operations import AnyOperation
    from test_tools.__private.account import Account
    from test_tools.__private.type_annotations.any_node import AnyNode
    from test_tools.__private.wallet.constants import TransactionSerializationTypes, WalletResponse, WalletResponseBase
    from test_tools.__private.wallet.single_transaction_context import SingleTransactionContext
    from wax.helpy import Hf26Asset as Asset


class WalletHandle(Handle):
    def __init__(
        self,
        attach_to: AnyNode | None = None,
        preconfigure: bool = True,
        chain_id: Hex | str = "default",
        transaction_serialization: TransactionSerializationTypes = "hf26",
    ):
        """
        Prepare environment for wallet based on instance of beekeeper and wax, runs beekeeper instance, beekeeper session and wallet and made preconfigurations for test usage.

        :param attach_to: Wallet will send messages to node passed as this parameter. Passing node is optional, but when
            node is omitted, wallet functionalities are limited.
        :param preconfigure: If set to True, after run wallet initminer's keys imported.
        :param chain_id: If set to "default", wallet use chain_id from node, else use typed chain_id.
        :param transaction_serialization: Set type of transaction serialization- hf26 or legacy. Default: hf26. Legacy serialization may not work correctly with the testnet.
        """
        if isinstance(attach_to, NodeHandleBase | RemoteNodeHandle):
            attach_to = get_implementation(attach_to, Node | RemoteNode)  # type: ignore[arg-type]

        super().__init__(
            implementation=Wallet(
                attach_to=attach_to,
                preconfigure=preconfigure,
                chain_id=chain_id,
                transaction_serialization=transaction_serialization,
            )
        )

        self.api = self.__implementation.api

    @property
    def __implementation(self) -> Wallet:  # type: ignore[override]  # this is forward of base class private member to child private member
        return get_implementation(self, Wallet)

    @property
    def connected_node(self) -> None | Node | RemoteNode:
        """Returns node instance connected to the wallet."""
        return self.__implementation.connected_node

    def in_single_transaction(self, *, broadcast: bool = True, blocking: bool = True) -> SingleTransactionContext:
        """
        Returns context manager allowing aggregation of multiple operations to single transaction.

        Must be used within `with` statement. All operations from API calls within this
        context are grouped to single transaction and optionally sent to blockchain at exit from context.

        :param broadcast: If set to True, this is default behavior, sends (broadcasts) transaction to blockchain.
            If set to False, only builds transaction without sending, which may be accessed with `get_response` method
            of returned context manager object.
            Otherwise behavior is undefined.
        :param blocking: If set to True, wallet waiting for response from blockchain. If set to False, directly after send request, program continue working.
        """
        return self.__implementation.in_single_transaction(broadcast=broadcast, blocking=blocking)

    def send(
        self, operations: list[AnyOperation], broadcast: bool, blocking: bool = True
    ) -> WalletResponseBase | WalletResponse | None:
        """
        Enable to sign and send transaction with any operations.

        :param: operations: List of operation, which have to be send in this transaction.
        :param broadcast: If set to True, this is default behavior, sends (broadcasts) transaction to blockchain.
            If set to False, only builds transaction without sending.
        :param blocking: If set to True, wallet waiting for response from blockchain. If set to False, directly after send request, program continue working.
        """
        return self.__implementation.send(operations=operations, broadcast=broadcast, blocking=blocking)

    def run(self, preconfigure: bool = True) -> None:
        """
        Runs beekeeper instance, beekeeper session and wallet. Also makes preconfigurations for test usage.

        :param preconfigure: If set to True, after run wallet initminer's keys imported.
        """
        self.__implementation.run(preconfigure=preconfigure)

    def restart(self) -> None:
        """Close wallet and run it again."""
        self.__implementation.restart()

    def close(self) -> None:
        """Remove beekeeper instance, close beekeeper session and performs needed cleanups."""
        self.__implementation.close()

    def is_running(self) -> bool:
        """Returns True if wallet is running, otherwise False."""
        return self.__implementation.is_running()

    def create_accounts(
        self, number_of_accounts: int, name_base: str = "account", *, secret: str = "secret", import_keys: bool = True
    ) -> list[Account]:
        """
        Creates accounts in blockchain.

        :param number_of_accounts: Number of accounts to create.
        :param name_base: All account names are generated as "<name_base>-<index>",
                          e.g.: account-0, account-1, account-2 and so on...
        :param secret: Text using as seed for account keys generation.
        :param import_keys: If set to true, imports created accounts' private keys. These keys are needed if you want to
                            create and sign transactions with previously created accounts.
        :return: List of created accounts.
        """
        return self.__implementation.create_accounts(
            number_of_accounts, name_base, secret=secret, import_keys=import_keys
        )

    def list_accounts(self) -> list[str]:
        """
        Gets names of all accounts in blockchain.

        :return: List of account names.
        """
        return self.__implementation.list_accounts()

    def create_account(
        self,
        name: str,
        *,
        creator: str = "initminer",
        hives: Asset.TestT | float | None = None,
        vests: Asset.TestT | float | None = None,
        hbds: Asset.TbdT | float | None = None,
    ) -> WalletResponseBase | WalletResponse | None:
        """
        Creates account in blockchain and optionally fund it with given amount of hives, vests and HBDs.

        :param name: Name of new account that will be created and broadcasted to blockchain.
        :param creator: Name of account, which requests creation of another account.
        :param hives: Hives that will be transferred to the newly created account.
        :param vests: Vests that will be transferred to the newly created account.
        :param hbds: HBDs that will be transferred to the newly created account.
        :return: Transaction which created account.
        """
        return self.__implementation.create_account(name, creator=creator, hives=hives, vests=vests, hbds=hbds)

    @property
    def directory(self) -> Path:
        """Returns path to directory containing files generated by wallet."""
        return self.__implementation.directory
