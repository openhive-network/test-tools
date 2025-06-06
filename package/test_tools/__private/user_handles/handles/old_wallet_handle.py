# mypy: ignore-errors
# ruff: noqa
# file for deletion after cli_wallet deprecation
from __future__ import annotations

import typing
from typing import TYPE_CHECKING, Literal
from test_tools.__private.type_annotations.any_node import AnyNode

from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.user_handles.handle import Handle
from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase
from test_tools.__private.user_handles.handles.node_handles.remote_node_handle import RemoteNodeHandle as RemoteNode
from test_tools.__private.old_wallet import SingleTransactionContext, OldWallet

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from wax.helpy import Hf26Asset as Asset
    from test_tools.__private.account import Account


class OldWalletHandle(Handle):
    DEFAULT_PASSWORD = OldWallet.DEFAULT_PASSWORD

    def __init__(
        self,
        attach_to: AnyNode | None = None,
        additional_arguments: Iterable[str] = (),
        preconfigure: bool = True,
        time_control: str | None = None,
    ):
        """
        Creates wallet, runs its process and blocks until wallet will be ready to use.

        :param attach_to: OldWallet will send messages to node passed as this parameter. Passing node is optional, but when
            node is omitted, wallet functionalities are limited.
        :param additional_arguments: Command line arguments which will be applied during running wallet.
        :param preconfigure: If set to True, after run wallet will be unlocked with password DEFAULT_PASSWORD and
            initminer's keys imported.
        :param time_control: See parameter ``time_control`` in :func:`run`.
        """
        if isinstance(attach_to, NodeHandleBase | RemoteNode):
            attach_to = get_implementation(attach_to, AnyNode)

        super().__init__(
            implementation=OldWallet(
                attach_to=attach_to,
                additional_arguments=additional_arguments,
                preconfigure=preconfigure,
                time_control=time_control,
            )
        )

        self.api = self.__implementation.api

    @property
    def __implementation(self) -> OldWallet:
        return get_implementation(self, OldWallet)

    def in_single_transaction(self, *, broadcast: bool | None = None) -> SingleTransactionContext:
        """
        Returns context manager allowing aggregation of multiple operations to single transaction.

        Must be used within `with` statement. All operations from API calls within this
        context are grouped to single transaction and optionally sent to blockchain at exit from context.

        :param broadcast: If set to True, this is default behavior, sends (broadcasts) transaction to blockchain.
            If set to False, only builds transaction without sending, which may be accessed with `get_response` method
            of returned context manager object.
            Otherwise behavior is undefined.
        """
        return self.__implementation.in_single_transaction(broadcast=broadcast)

    def run(
        self,
        *,
        timeout: float = OldWallet.DEFAULT_RUN_TIMEOUT,
        preconfigure: bool = True,
        time_control: str | None = None,
    ):
        """
        Runs wallet's process and blocks until wallet will be ready to use.

        :param timeout: TimeoutError will be raised, if wallet won't start before specified timeout.
        :param preconfigure: If set to True, after run wallet will be unlocked with password DEFAULT_PASSWORD and
            initminer's keys imported.
        :param time_control: Allows to change system date and time a node sees (without changing real OS time).
            Can be specified either absolutely, relatively and speed up or slow down clock. Value passed in
            `time_control` is written to `FAKETIME` environment variable. For details and examples see libfaketime
            official documentation: https://github.com/wolfcw/libfaketime.
        """
        self.__implementation.run(timeout=timeout, preconfigure=preconfigure, time_control=time_control)

    def restart(self, *, preconfigure: bool = True, time_control: str | None = None) -> None:
        """
        Closes wallet's process, runs it again and blocks until wallet will be ready to use.

        :param preconfigure: If set to True, after run wallet will be unlocked with password DEFAULT_PASSWORD and
            initminer's keys imported.
        :param time_control: See parameter ``time_control`` in :func:`run`.
        """
        self.__implementation.restart(preconfigure=preconfigure, time_control=time_control)

    @property
    def transaction_serialization(self) -> Literal["legacy", "hf26"]:
        """
        Returns information about how transactions are serialized.

        Can be serialized in legacy way (e.g. assets are serialized as strings "3.000 HIVE", but it's not the only
        difference) or in HF26 way (then are serialized as {"amount": "3000", "precision": 3, "nai": "@@000000021"}).
        """
        return self.__implementation.transaction_serialization

    def close(self) -> None:
        """
        Terminates wallet's process and performs needed cleanups.

        Blocks until wallet process will be finished. Closing is performed by sending SIGINT signal.
        If wallet doesn't close before timeout, sends SIGKILL and emits warning message.
        """
        self.__implementation.close()

    def is_running(self) -> bool:
        """Returns True if wallet's process is running, otherwise False."""
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
    ) -> dict:
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
