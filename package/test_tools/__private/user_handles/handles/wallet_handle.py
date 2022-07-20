from __future__ import annotations

import typing
from typing import TYPE_CHECKING
from typing import Iterable
from typing import List
from typing import Union

from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.user_handles.handle import Handle
from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase
from test_tools.__private.user_handles.handles.node_handles.remote_node_handle import RemoteNodeHandle as RemoteNode
from test_tools.__private.wallet import Wallet

if TYPE_CHECKING:
    from pathlib import Path

    from test_tools.__private.account import Account


class WalletHandle(Handle):
    DEFAULT_PASSWORD = Wallet.DEFAULT_PASSWORD

    def __init__(
        self,
        attach_to: Union[None, NodeHandleBase, RemoteNode] = None,
        additional_arguments: Iterable[str] = (),
        preconfigure: bool = True,
    ):
        """
        Creates wallet, runs its process and blocks until wallet will be ready to use.

        :param attach_to: Wallet will send messages to node passed as this parameter. Passing node is optional, but when
            node is omitted, wallet functionalities are limited.
        :param additional_arguments: Command line arguments which will be applied during running wallet.
        :param preconfigure: If set to True, after run wallet will be unlocked with password DEFAULT_PASSWORD and
            initminer's keys imported.
        """
        if isinstance(attach_to, (NodeHandleBase, RemoteNode)):
            attach_to = get_implementation(attach_to)

        super().__init__(
            implementation=Wallet(
                attach_to=attach_to,
                additional_arguments=additional_arguments,
                preconfigure=preconfigure,
            )
        )

        self.api = self.__implementation.api

    @property
    def __implementation(self) -> Wallet:
        return typing.cast(Wallet, get_implementation(self))

    def in_single_transaction(self, *, broadcast: bool = None):
        """
        Returns context manager allowing aggregation of multiple operations to single transaction. Must be used within
        `with` statement. All operations from API calls within this context are grouped to single transaction and
        optionally sent to blockchain at exit from context.

        :param broadcast: If set to True, this is default behavior, sends (broadcasts) transaction to blockchain.
            If set to False, only builds transaction without sending, which may be accessed with `get_response` method
            of returned context manager object.
            Otherwise behavior is undefined.
        """

        return self.__implementation.in_single_transaction(broadcast=broadcast)

    def run(self, *, timeout: float = Wallet.DEFAULT_RUN_TIMEOUT, preconfigure: bool = True):
        """
        Runs wallet's process and blocks until wallet will be ready to use.

        :param timeout: TimeoutError will be raised, if wallet won't start before specified timeout.
        :param preconfigure: If set to True, after run wallet will be unlocked with password DEFAULT_PASSWORD and
            initminer's keys imported.
        """

        self.__implementation.run(timeout=timeout, preconfigure=preconfigure)

    def restart(self, *, preconfigure: bool = True):
        """
        Closes wallet's process, runs it again and blocks until wallet will be ready to use.

        :param preconfigure: If set to True, after run wallet will be unlocked with password DEFAULT_PASSWORD and
            initminer's keys imported.
        """

        self.__implementation.restart(preconfigure=preconfigure)

    def close(self):
        """
        Terminates wallet's process and performs needed cleanups. Blocks until wallet process will be finished. Closing
        is performed by sending SIGINT signal. If wallet doesn't close before timeout, sends SIGKILL and emits warning
        message.
        """

        self.__implementation.close()

    def is_running(self) -> bool:
        """
        Returns True if wallet's process is running, otherwise False.
        """

        return self.__implementation.is_running()

    def create_accounts(
        self, number_of_accounts: int, name_base: str = 'account', *, secret: str = 'secret', import_keys: bool = True
    ) -> List[Account]:
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

    def list_accounts(self) -> List[str]:
        """
        Gets names of all accounts in blockchain.

        :return: List of account names.
        """
        return self.__implementation.list_accounts()

    @property
    def directory(self) -> 'Path':
        """
        Returns path to directory containing files generated by wallet.
        """

        return self.__implementation.directory
