from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from helpy._interfaces.context import ContextSync
from test_tools.__private.wallet.constants import WalletResponse, WalletResponseBase

if TYPE_CHECKING:
    from test_tools.__private.node import Node
    from test_tools.__private.remote_node import RemoteNode

    AnyNode = Node | RemoteNode
    from test_tools.__private.wallet.wallet import Wallet


class SingleTransactionContext(ContextSync["SingleTransactionContext"]):
    def __init__(self, wallet_: Wallet, *, broadcast: bool, blocking: bool) -> None:
        self.__wallet = wallet_
        self.__broadcast = broadcast
        self.__blocking = blocking
        self.__response: WalletResponseBase | WalletResponse | None = None
        self.__was_run_as_context_manager = False

    def get_response(self) -> None | WalletResponseBase | WalletResponse:
        return self.__response

    def as_dict(self) -> None | dict[str, Any]:
        if isinstance(self.__response, WalletResponseBase | WalletResponse):
            return self.__response.__dict__
        return None

    def __del__(self) -> None:
        if not self.__was_run_as_context_manager:
            from test_tools.__private.wallet.wallet import Wallet

            raise RuntimeError(
                f'You used {Wallet.__name__}.{Wallet.in_single_transaction.__name__}() not in "with" statement'
            )

    def _enter(self) -> SingleTransactionContext:
        self.__wallet.api._start_gathering_operations_for_single_transaction()
        self.__was_run_as_context_manager = True
        return self

    def _finally(self) -> None:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_value is not None:
            raise exc_value
        self.__response = self.__wallet.api._send_gathered_operations_as_single_transaction(
            broadcast=self.__broadcast, blocking=self.__blocking
        )
