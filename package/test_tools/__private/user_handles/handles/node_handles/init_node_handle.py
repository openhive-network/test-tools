from __future__ import annotations

from typing import TYPE_CHECKING

from helpy import Hf26Asset as Asset
from test_tools.__private.init_node import InitNode
from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.user_handles.handles.node_handles.runnable_node_handle import RunnableNodeHandle

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle as Network


class InitNodeHandle(RunnableNodeHandle):
    def __init__(self, network: Network | None = None) -> None:
        super().__init__(
            implementation=InitNode(
                network=network,
                handle=self,
            )
        )

    @property
    def __implementation(self) -> InitNode:  # type: ignore[override]
        return get_implementation(self, InitNode)

    def set_vest_price(
        self,
        quote: Asset.Vests,
        base: Asset.Test = Asset.test(1),  # noqa: B008
        invest: Asset.Test = Asset.test(10_000_000),  # noqa: B008
    ) -> None:
        """
        Used to set a new price for vests in relation to hive on a blockchain node.

        It calculates the new price, logs it, and then updates the vest price on the node using the API call.
        :param invest: The hive amount to be invested in the network to mitigate inflation during the price change.
        :param base: The base asset for the price calculation (hive).
        :param quote: The quote asset for the price calculation (vests).
        :raises RuntimeError: When the node is not running.
        """
        self.__implementation.set_vest_price(base, quote, invest)
